import shutil
import subprocess
import re
from typing import Tuple, List, Optional
import psutil

class SystemService:
    @staticmethod
    def get_ffmpeg_path() -> Optional[str]:
        return shutil.which("ffmpeg")

    @staticmethod
    def get_ffprobe_path() -> Optional[str]:
        return shutil.which("ffprobe")

    @classmethod
    def check_ffmpeg_capabilities(cls) -> Tuple[bool, Optional[str], bool, List[str]]:
        """
        Returns (is_available, version_string, is_nvenc_available, list_of_supported_encoders)
        """
        ffmpeg_bin = cls.get_ffmpeg_path()
        if not ffmpeg_bin:
            return False, None, False, []

        version_str = "unknown"
        supported_encoders = []
        is_nvenc = False

        try:
            # 1. Check version
            res = subprocess.run([ffmpeg_bin, "-version"], capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                first_line = res.stdout.splitlines()[0] if res.stdout else ""
                match = re.search(r"ffmpeg version\s+([^\s]+)", first_line)
                if match:
                    version_str = match.group(1)
                else:
                    version_str = first_line

            # 2. Check encoders
            res = subprocess.run([ffmpeg_bin, "-encoders"], capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                output = res.stdout
                if "h264_nvenc" in output:
                    supported_encoders.append("h264_nvenc")
                    is_nvenc = True
                if "hevc_nvenc" in output:
                    supported_encoders.append("hevc_nvenc")
                if "libx264" in output:
                    supported_encoders.append("libx264")
        except Exception:
            return True, version_str, False, []

        return True, version_str, is_nvenc, supported_encoders

    @staticmethod
    def detect_nvidia_gpu() -> Tuple[bool, Optional[str]]:
        nvidia_smi = shutil.which("nvidia-smi")
        if not nvidia_smi:
            return False, None

        try:
            res = subprocess.run(
                [nvidia_smi, "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if res.returncode == 0 and res.stdout.strip():
                gpu_names = [line.strip() for line in res.stdout.splitlines() if line.strip()]
                return True, ", ".join(gpu_names)
        except Exception:
            pass
        return False, None

    @staticmethod
    def get_disk_free(path: str) -> int:
        try:
            usage = shutil.disk_usage(path)
            return usage.free
        except Exception:
            return 0

    @staticmethod
    def get_cpu_cores() -> int:
        return psutil.cpu_count(logical=True) or 1
