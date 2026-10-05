import asyncio
import time
import uuid
import logging
from pathlib import Path
from typing import Dict, Optional, List, Set
from fastapi import WebSocket
from shared.schemas import JobStatus
from server.app.services.ffmpeg_service import FFmpegService
from server.app.services.checksum_service import compute_file_sha256
from server.app.services.system_service import SystemService
from server.app.config import settings

logger = logging.getLogger("job_manager")

class Job:
    def __init__(
        self,
        job_id: str,
        input_filename: str,
        output_filename: str,
        job_dir: Path,
        resolution: str,
        bitrate: str,
        preset: str,
        checksum: str,
        allow_cpu_fallback: bool = False
    ):
        self.job_id = job_id
        self.input_filename = input_filename
        self.output_filename = output_filename
        self.job_dir = job_dir
        self.resolution = resolution
        self.bitrate = bitrate
        self.preset = preset
        self.input_checksum = checksum
        self.allow_cpu_fallback = allow_cpu_fallback

        self.input_path = job_dir / "input" / input_filename
        self.output_path = job_dir / "output" / output_filename
        self.log_path = job_dir / "render.log"

        self.status = JobStatus.QUEUED
        self.created_at = time.time()
        self.start_time: Optional[float] = None
        self.finish_time: Optional[float] = None
        self.duration_total_sec: Optional[float] = None

        self.progress_percent: float = 0.0
        self.elapsed_seconds: float = 0.0
        self.eta_seconds: Optional[float] = None
        self.speed: Optional[str] = None
        self.current_fps: Optional[float] = None
        self.output_size_bytes: int = 0
        self.output_checksum: Optional[str] = None
        self.error_message: Optional[str] = None

        self.process: Optional[asyncio.subprocess.Process] = None
        self._cancelled: bool = False

class JobManager:
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.active_subscribers: Dict[str, Set[WebSocket]] = {}
        self.semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_JOBS)
        self.lock = asyncio.Lock()

    async def create_job(
        self,
        input_filename: str,
        output_filename: str,
        resolution: str,
        bitrate: str,
        preset: str,
        checksum: str,
        file_size: int,
        allow_cpu_fallback: bool = False
    ) -> Job:
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        job_dir = settings.storage_path / job_id
        (job_dir / "input").mkdir(parents=True, exist_ok=True)
        (job_dir / "output").mkdir(parents=True, exist_ok=True)

        job = Job(
            job_id=job_id,
            input_filename=input_filename,
            output_filename=output_filename,
            job_dir=job_dir,
            resolution=resolution,
            bitrate=bitrate,
            preset=preset,
            checksum=checksum,
            allow_cpu_fallback=allow_cpu_fallback
        )

        async with self.lock:
            self.jobs[job_id] = job
            self.active_subscribers[job_id] = set()

        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        return self.jobs.get(job_id)

    async def subscribe(self, job_id: str, websocket: WebSocket):
        async with self.lock:
            if job_id not in self.active_subscribers:
                self.active_subscribers[job_id] = set()
            self.active_subscribers[job_id].add(websocket)

    async def unsubscribe(self, job_id: str, websocket: WebSocket):
        async with self.lock:
            if job_id in self.active_subscribers:
                self.active_subscribers[job_id].discard(websocket)

    async def broadcast(self, job_id: str, message: dict):
        subscribers = list(self.active_subscribers.get(job_id, []))
        for ws in subscribers:
            try:
                await ws.send_json(message)
            except Exception:
                await self.unsubscribe(job_id, ws)

    async def cancel_job(self, job_id: str) -> bool:
        job = self.get_job(job_id)
        if not job:
            return False
        
        job._cancelled = True
        job.status = JobStatus.CANCELLED
        job.error_message = "Cancelled by user request."

        if job.process and job.process.returncode is None:
            try:
                job.process.terminate()
                await asyncio.sleep(0.5)
                if job.process.returncode is None:
                    job.process.kill()
            except Exception as e:
                logger.error(f"Error terminating process for job {job_id}: {e}")

        await self.broadcast(job_id, {
            "type": "state",
            "job_id": job_id,
            "status": JobStatus.CANCELLED,
            "message": "Render job was cancelled."
        })
        return True

    async def start_render_job(self, job: Job):
        asyncio.create_task(self._run_render_worker(job))

    async def _run_render_worker(self, job: Job):
        async with self.semaphore:
            if job._cancelled:
                return

            job.status = JobStatus.RENDERING
            job.start_time = time.time()
            await self.broadcast(job.job_id, {
                "type": "state",
                "job_id": job.job_id,
                "status": JobStatus.RENDERING,
                "message": "Rendering started."
            })

            # Check FFmpeg and NVENC capabilities
            is_avail, _, is_nvenc, _ = SystemService.check_ffmpeg_capabilities()
            if not is_avail:
                job.status = JobStatus.FAILED
                job.error_message = (
                    "FFmpeg is not installed on the worker system or not found in system PATH. "
                    "Please install FFmpeg (e.g., download from ffmpeg.org or run 'winget install Gyan.FFmpeg') on the worker computer."
                )
                await self.broadcast(job.job_id, {
                    "type": "error",
                    "job_id": job.job_id,
                    "status": JobStatus.FAILED,
                    "error": job.error_message
                })
                return

            use_nvenc = is_nvenc
            if not is_nvenc:
                if not job.allow_cpu_fallback and not settings.ALLOW_CPU_FALLBACK:
                    job.status = JobStatus.FAILED
                    job.error_message = (
                        "NVIDIA NVENC hardware encoding is not available on worker server. "
                        "Job aborted because CPU fallback is disabled."
                    )
                    await self.broadcast(job.job_id, {
                        "type": "error",
                        "job_id": job.job_id,
                        "status": JobStatus.FAILED,
                        "error": job.error_message
                    })
                    return
                else:
                    use_nvenc = False
                    await self.broadcast(job.job_id, {
                        "type": "log",
                        "job_id": job.job_id,
                        "level": "WARNING",
                        "message": "NVENC not available. Falling back to CPU encoder (libx264) as requested."
                    })

            # Probe duration for progress calculation
            video_duration = FFmpegService.get_video_duration(job.input_path)
            job.duration_total_sec = video_duration

            # Build command
            cmd = FFmpegService.build_ffmpeg_command(
                input_path=job.input_path,
                output_path=job.output_path,
                resolution=job.resolution,
                bitrate=job.bitrate,
                preset=job.preset,
                use_nvenc=use_nvenc
            )

            await self.broadcast(job.job_id, {
                "type": "log",
                "job_id": job.job_id,
                "level": "INFO",
                "message": f"FFmpeg command: {' '.join(cmd)}"
            })

            try:
                with open(job.log_path, "w", encoding="utf-8") as log_file:
                    log_file.write(f"FFmpeg command: {' '.join(cmd)}\n\n")

                job.process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                # Read progress and stderr concurrently
                progress_task = asyncio.create_task(self._stream_progress(job))
                stderr_task = asyncio.create_task(self._stream_stderr(job))

                await asyncio.gather(progress_task, stderr_task)
                await job.process.wait()

                if job._cancelled:
                    job.status = JobStatus.CANCELLED
                    return

                if job.process.returncode == 0 and job.output_path.exists() and job.output_path.stat().st_size > 0:
                    job.status = JobStatus.COMPLETED
                    job.finish_time = time.time()
                    job.progress_percent = 100.0
                    job.output_size_bytes = job.output_path.stat().st_size
                    job.output_checksum = compute_file_sha256(job.output_path)
                    total_time = round(job.finish_time - job.start_time, 2)

                    await self.broadcast(job.job_id, {
                        "type": "state",
                        "job_id": job.job_id,
                        "status": JobStatus.COMPLETED,
                        "output_checksum": job.output_checksum,
                        "output_size_bytes": job.output_size_bytes,
                        "total_render_seconds": total_time,
                        "message": "Rendering completed successfully."
                    })
                else:
                    job.status = JobStatus.FAILED
                    if not job.error_message:
                        job.error_message = f"FFmpeg exited with non-zero code {job.process.returncode}."
                    await self.broadcast(job.job_id, {
                        "type": "error",
                        "job_id": job.job_id,
                        "status": JobStatus.FAILED,
                        "error": job.error_message
                    })
            except Exception as e:
                logger.exception("Error executing FFmpeg subprocess")
                job.status = JobStatus.FAILED
                job.error_message = str(e)
                await self.broadcast(job.job_id, {
                    "type": "error",
                    "job_id": job.job_id,
                    "status": JobStatus.FAILED,
                    "error": str(e)
                })

    async def _stream_progress(self, job: Job):
        if not job.process or not job.process.stdout:
            return

        while True:
            line = await job.process.stdout.readline()
            if not line:
                break
            text = line.decode("utf-8", errors="replace").strip()
            if not text:
                continue

            parsed = FFmpegService.parse_progress_line(text)
            if not parsed:
                continue

            # Check key progress indicators
            if "out_time_ms" in parsed or "out_time_us" in parsed or "out_time" in parsed:
                raw_time = parsed.get("out_time_us") or parsed.get("out_time_ms") or parsed.get("out_time")
                current_sec = FFmpegService.parse_time_to_seconds(raw_time)

                if job.start_time:
                    job.elapsed_seconds = round(time.time() - job.start_time, 1)

                if job.duration_total_sec and job.duration_total_sec > 0:
                    pct = min(100.0, round((current_sec / job.duration_total_sec) * 100.0, 1))
                    job.progress_percent = pct
                    # Calculate ETA
                    if pct > 0:
                        remaining_ratio = (100.0 - pct) / pct
                        job.eta_seconds = round(job.elapsed_seconds * remaining_ratio, 1)

                if "speed" in parsed:
                    job.speed = parsed["speed"]
                if "fps" in parsed:
                    try:
                        job.current_fps = float(parsed["fps"])
                    except Exception:
                        pass

                await self.broadcast(job.job_id, {
                    "type": "progress",
                    "job_id": job.job_id,
                    "status": job.status,
                    "percent": job.progress_percent,
                    "elapsed_seconds": job.elapsed_seconds,
                    "eta_seconds": job.eta_seconds,
                    "speed": job.speed,
                    "fps": job.current_fps
                })

    async def _stream_stderr(self, job: Job):
        if not job.process or not job.process.stderr:
            return

        with open(job.log_path, "a", encoding="utf-8") as f:
            while True:
                line = await job.process.stderr.readline()
                if not line:
                    break
                text = line.decode("utf-8", errors="replace").strip()
                if text:
                    f.write(text + "\n")
                    f.flush()
                    # Broadcast stderr lines as log messages
                    await self.broadcast(job.job_id, {
                        "type": "log",
                        "job_id": job.job_id,
                        "level": "INFO",
                        "message": text
                    })

job_manager = JobManager()
