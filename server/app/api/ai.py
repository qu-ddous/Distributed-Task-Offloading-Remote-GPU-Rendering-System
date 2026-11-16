"""
FastAPI Router for GPUShare AI Training & Google Lens Inference
Mounted under /api/v1/ai
"""

import uuid
import shutil
import asyncio
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, Header, HTTPException, Request, status, BackgroundTasks
from fastapi.responses import JSONResponse

from server.app.services.ai_service import ai_service
from server.app.services.security import sanitize_filename
from server.app.config import settings

router = APIRouter()

def verify_token(x_api_token: Optional[str] = Header(None)):
    if settings.API_TOKEN and x_api_token != settings.API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Token header."
        )

@router.get("/status")
async def get_ai_status():
    """Returns AI hardware capabilities, CUDA device info, and current training status"""
    return ai_service.get_hardware_status()

@router.post("/train")
async def start_training(
    background_tasks: BackgroundTasks,
    model_arch: str = Form("resnet"),
    epochs: int = Form(5),
    batch_size: int = Form(64),
    learning_rate: float = Form(0.001),
    optimizer: str = Form("adam"),
    use_gpu: bool = Form(True),
    dataset_path: Optional[str] = Form(None),
    x_api_token: Optional[str] = Header(None)
):
    """
    Spawns background PyTorch CNN training job on Server GPU.
    """
    verify_token(x_api_token)

    if ai_service.is_training:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An AI model training job is already actively running on the GPU."
        )

    job_id = f"ai_{uuid.uuid4().hex[:8]}"

    # Run training in background thread pool so FastAPI remains fully responsive
    loop = asyncio.get_event_loop()
    background_tasks.add_task(
        loop.run_in_executor,
        None,
        ai_service.run_training_sync,
        job_id,
        model_arch,
        epochs,
        batch_size,
        learning_rate,
        optimizer,
        use_gpu,
        dataset_path
    )

    return {
        "success": True,
        "job_id": job_id,
        "message": f"Training job '{job_id}' started on Server hardware ({model_arch.upper()}, {epochs} epochs).",
        "model_architecture": model_arch
    }

@router.post("/cancel")
async def cancel_training(x_api_token: Optional[str] = Header(None)):
    """Cancels active training job"""
    verify_token(x_api_token)
    ai_service.cancel_training()
    return {"success": True, "message": "Training cancellation requested."}

@router.get("/progress")
async def get_training_progress():
    """Returns real-time training telemetry, loss, accuracy, and console logs"""
    return {
        "is_training": ai_service.is_training,
        "stats": ai_service.training_stats,
        "recent_logs": ai_service.log_history[-10:] if ai_service.log_history else []
    }

@router.post("/predict")
async def predict_image(
    file: UploadFile = File(...),
    x_api_token: Optional[str] = Header(None)
):
    """
    Google Lens Style Neural Vision Inference.
    Uploads an image, processes through trained CNN on GPU, returns class and confidence.
    """
    verify_token(x_api_token)

    clean_filename = sanitize_filename(file.filename or "lens_query.jpg")
    temp_dir = settings.storage_path / "temp_lens"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / clean_filename

    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Execute Google Lens Inference on GPU
        result = ai_service.predict_image(str(temp_path))
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(e)}"
        )
    finally:
        # Clean up temporary query image
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass

@router.post("/benchmark")
async def run_benchmark(x_api_token: Optional[str] = Header(None)):
    """
    Runs CPU vs GPU comparative performance test as required by assignment
    """
    verify_token(x_api_token)
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, ai_service.run_hardware_benchmark)
    return result
