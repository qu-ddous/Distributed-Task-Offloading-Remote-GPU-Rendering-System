import os
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, Header, HTTPException, status
from fastapi.responses import FileResponse
from shared.schemas import JobCreateResponse, JobStatusResponse, CancelResponse
from server.app.services.job_manager import job_manager
from server.app.services.security import sanitize_filename, validate_path_safety
from server.app.config import settings

router = APIRouter()

def verify_token(x_api_token: str):
    if settings.API_TOKEN and x_api_token != settings.API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Token header."
        )

@router.post("", response_model=JobCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    file: UploadFile = File(...),
    checksum: str = Form(...),
    resolution: str = Form("Original"),
    bitrate: str = Form("5M"),
    preset: str = Form("p4"),
    output_filename: str = Form(...),
    allow_cpu_fallback: bool = Form(False),
    x_api_token: str = Header(None)
):
    verify_token(x_api_token)

    clean_input_name = sanitize_filename(file.filename or "input.mp4")
    clean_output_name = sanitize_filename(output_filename or f"rendered_{clean_input_name}")

    # Prepare job
    job = await job_manager.create_job(
        input_filename=clean_input_name,
        output_filename=clean_output_name,
        resolution=resolution,
        bitrate=bitrate,
        preset=preset,
        checksum=checksum,
        file_size=0,
        allow_cpu_fallback=allow_cpu_fallback
    )

    # Stream file to disk and compute sha256
    hasher = hashlib.sha256()
    total_bytes = 0

    try:
        with open(job.input_path, "wb") as out_f:
            while chunk := await file.read(1024 * 1024): # 1MB chunks
                total_bytes += len(chunk)
                if total_bytes > settings.MAX_UPLOAD_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Uploaded file exceeds maximum limit of {settings.MAX_UPLOAD_SIZE} bytes."
                    )
                hasher.update(chunk)
                out_f.write(chunk)
    except Exception as e:
        # Cleanup incomplete upload
        if job.input_path.exists():
            job.input_path.unlink(missing_ok=True)
        raise e

    # Verify checksum
    server_checksum = hasher.hexdigest().lower()
    if server_checksum != checksum.strip().lower():
        if job.input_path.exists():
            job.input_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Integrity check failed: Client SHA-256 ({checksum}) != Server SHA-256 ({server_checksum})."
        )

    # Start rendering asynchronously
    await job_manager.start_render_job(job)

    return JobCreateResponse(
        job_id=job.job_id,
        status=job.status,
        created_at=datetime.now(timezone.utc).isoformat(),
        input_filename=job.input_filename,
        output_filename=job.output_filename,
        file_size=total_bytes,
        checksum=server_checksum
    )

@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str, x_api_token: str = Header(None)):
    verify_token(x_api_token)
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress_percent=job.progress_percent,
        elapsed_seconds=job.elapsed_seconds,
        eta_seconds=job.eta_seconds,
        speed=job.speed,
        current_fps=job.current_fps,
        output_ready=job.output_path.exists() and job.status.value == "completed",
        output_size_bytes=job.output_size_bytes,
        output_checksum=job.output_checksum,
        error_message=job.error_message
    )

@router.post("/{job_id}/cancel", response_model=CancelResponse)
async def cancel_job(job_id: str, x_api_token: str = Header(None)):
    verify_token(x_api_token)
    success = await job_manager.cancel_job(job_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    return CancelResponse(
        job_id=job_id,
        status=job_manager.get_job(job_id).status,
        message="Render job cancelled successfully."
    )

@router.get("/{job_id}/download")
async def download_output(job_id: str, x_api_token: str = Header(None)):
    verify_token(x_api_token)
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    if not job.output_path.exists():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Output file is not ready yet or render failed.")

    # Validate directory safety
    if not validate_path_safety(job.job_dir / "output", job.output_path):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Path traversal violation.")

    headers = {
        "X-Checksum-SHA256": job.output_checksum or "",
        "Content-Disposition": f'attachment; filename="{job.output_filename}"'
    }

    return FileResponse(
        path=str(job.output_path),
        filename=job.output_filename,
        media_type="application/octet-stream",
        headers=headers
    )
