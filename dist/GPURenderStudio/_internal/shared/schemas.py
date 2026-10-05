"""
Shared constants, schemas, and protocol definitions across client and server.
"""
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

PROTOCOL_VERSION = "v1.0.0"

class JobStatus(str, Enum):
    QUEUED = "queued"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ResolutionPreset(str, Enum):
    ORIGINAL = "Original"
    P720 = "720p"
    P1080 = "1080p"
    P1440 = "1440p"
    P4K = "4K"

    @property
    def scale_filter(self) -> Optional[str]:
        if self == ResolutionPreset.P720:
            return "scale=-2:720"
        elif self == ResolutionPreset.P1080:
            return "scale=-2:1080"
        elif self == ResolutionPreset.P1440:
            return "scale=-2:1440"
        elif self == ResolutionPreset.P4K:
            return "scale=-2:2160"
        return None

class NvencPreset(str, Enum):
    # Standard NVENC presets p1 (fastest/lowest quality) to p7 (slowest/highest quality)
    P1 = "p1"
    P2 = "p2"
    P3 = "p3"
    P4 = "p4" # default medium
    P5 = "p5"
    P6 = "p6"
    P7 = "p7"
    FAST = "fast"
    MEDIUM = "medium"
    SLOW = "slow"

class FFmpegInfo(BaseModel):
    available: bool
    version: Optional[str] = None
    nvenc_available: bool = False
    supported_encoders: List[str] = Field(default_factory=list)

class HardwareInfo(BaseModel):
    gpu_detected: bool = False
    gpu_name: Optional[str] = None
    cpu_cores: int = 1
    disk_free_bytes: int = 0

class ServerLimits(BaseModel):
    max_upload_size_bytes: int
    max_concurrent_jobs: int
    active_jobs: int

class HealthResponse(BaseModel):
    status: str = "online"
    protocol_version: str = PROTOCOL_VERSION
    server_time: str
    ffmpeg: FFmpegInfo
    hardware: HardwareInfo
    limits: ServerLimits

class LatencyPingResponse(BaseModel):
    pong: bool = True
    timestamp: float

class JobCreateResponse(BaseModel):
    job_id: str
    status: JobStatus = JobStatus.QUEUED
    created_at: str
    input_filename: str
    output_filename: str
    file_size: int
    checksum: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress_percent: float = 0.0
    elapsed_seconds: float = 0.0
    eta_seconds: Optional[float] = None
    speed: Optional[str] = None
    current_fps: Optional[float] = None
    output_ready: bool = False
    output_size_bytes: int = 0
    output_checksum: Optional[str] = None
    error_message: Optional[str] = None

class CancelResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str
