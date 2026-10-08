import time
from datetime import datetime, timezone
from fastapi import APIRouter, Header, HTTPException, status
from shared.schemas import HealthResponse, LatencyPingResponse, FFmpegInfo, HardwareInfo, ServerLimits
from server.app.services.system_service import SystemService
from server.app.services.job_manager import job_manager
from server.app.config import settings

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check(x_api_token: str = Header(None)):
    if settings.API_TOKEN and x_api_token != settings.API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Token header."
        )

    is_ff_avail, ff_ver, is_nvenc, encoders = SystemService.check_ffmpeg_capabilities()
    hw_data = SystemService.get_hardware_telemetry(str(settings.storage_path))
    active_count = sum(1 for j in job_manager.jobs.values() if j.status.value in ["queued", "rendering"])

    return HealthResponse(
        status="online",
        server_time=datetime.now(timezone.utc).isoformat(),
        ffmpeg=FFmpegInfo(
            available=is_ff_avail,
            version=ff_ver,
            nvenc_available=is_nvenc,
            supported_encoders=encoders
        ),
        hardware=HardwareInfo(
            hostname=hw_data["hostname"],
            os_platform=hw_data["os_platform"],
            cpu_model=hw_data["cpu_model"],
            cpu_cores=hw_data["cpu_cores"],
            cpu_percent=hw_data["cpu_percent"],
            ram_total_gb=hw_data["ram_total_gb"],
            ram_used_gb=hw_data["ram_used_gb"],
            ram_percent=hw_data["ram_percent"],
            disk_total_bytes=hw_data["disk_total_bytes"],
            disk_free_bytes=hw_data["disk_free_bytes"],
            gpu_detected=hw_data["gpu_detected"],
            gpu_name=hw_data["gpu_name"],
            gpu_vram_total_mb=hw_data["gpu_vram_total_mb"],
            gpu_vram_used_mb=hw_data["gpu_vram_used_mb"],
            gpu_util_percent=hw_data["gpu_util_percent"]
        ),
        limits=ServerLimits(
            max_upload_size_bytes=settings.MAX_UPLOAD_SIZE,
            max_concurrent_jobs=settings.MAX_CONCURRENT_JOBS,
            active_jobs=active_count
        )
    )

@router.get("/ping", response_model=LatencyPingResponse)
async def ping():
    return LatencyPingResponse(
        pong=True,
        timestamp=time.time()
    )
