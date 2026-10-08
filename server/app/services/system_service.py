import os
import shutil
import subprocess
import re
import socket
from typing import Tuple, List, Optional, Dict, Any
import psutil

# Windows process creation flag to completely prevent popup/flashing black console windows
CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0

class SystemService:
    _cached_ffmpeg_caps: Optional[Tuple[bool, Optional[str], bool, List[str]]] = None
    _cached_cpu_name: Optional[str] = None

    @staticmethod
    def get_ffmpeg_path() -> Optional[str]:
        # 1. System PATH
        bin_path = shutil.which("ffmpeg")
        if bin_path:
            return bin_path
        # 2. Embedded imageio-ffmpeg binary
        try:
            import imageio_ffmpeg
            exe = imageio_ffmpeg.get_ffmpeg_exe()
            if exe and os.path.exists(exe):
                return exe
        except Exception:
            pass
        return None

    @staticmethod
    def get_ffprobe_path() -> Optional[str]:
        return shutil.which("ffprobe")

    @classmethod
    def check_ffmpeg_capabilities(cls, force_refresh: bool = False) -> Tuple[bool, Optional[str], bool, List[str]]:
        """
        Returns (is_available, version_string, is_nvenc_available, list_of_supported_encoders)
        Caches capabilities to avoid repeating slow subprocess checks.
        Uses CREATE_NO_WINDOW so no black console ever flashes.
        """
        if cls._cached_ffmpeg_caps and not force_refresh:
            return cls._cached_ffmpeg_caps

        ffmpeg_bin = cls.get_ffmpeg_path()
        if not ffmpeg_bin:
            cls._cached_ffmpeg_caps = (False, None, False, [])
            return cls._cached_ffmpeg_caps

        version_str = "unknown"
        supported_encoders = []
        is_nvenc = False

        try:
            # 1. Check version
            res = subprocess.run(
                [ffmpeg_bin, "-version"],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=CREATE_NO_WINDOW
            )
            if res.returncode == 0:
                first_line = res.stdout.splitlines()[0] if res.stdout else ""
                match = re.search(r"ffmpeg version\s+([^\s]+)", first_line)
                if match:
                    version_str = match.group(1)
                else:
                    version_str = first_line

            # 2. Check encoders
            res = subprocess.run(
                [ffmpeg_bin, "-encoders"],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=CREATE_NO_WINDOW
            )
            if res.returncode == 0:
                output = res.stdout
                if "hevc_nvenc" in output:
                    supported_encoders.append("hevc_nvenc")
                if "libx264" in output:
                    supported_encoders.append("libx264")

                # Test if NVENC actually works on current hardware
                if "h264_nvenc" in output:
                    if shutil.which("nvidia-smi"):
                        test_nvenc = subprocess.run(
                            [ffmpeg_bin, "-f", "lavfi", "-i", "nullsrc=s=64x64:d=0.1", "-c:v", "h264_nvenc", "-f", "null", "-"],
                            capture_output=True,
                            text=True,
                            timeout=3,
                            creationflags=CREATE_NO_WINDOW
                        )
                        if test_nvenc.returncode == 0:
                            supported_encoders.insert(0, "h264_nvenc")
                            is_nvenc = True
        except Exception:
            cls._cached_ffmpeg_caps = (True, version_str, False, [])
            return cls._cached_ffmpeg_caps

        cls._cached_ffmpeg_caps = (True, version_str, is_nvenc, supported_encoders)
        return cls._cached_ffmpeg_caps

    _cached_static_specs: Optional[Dict[str, Any]] = None
    _cached_gpu_telemetry: Optional[Tuple[float, Dict[str, Any]]] = None

    @classmethod
    def get_static_specs(cls) -> Dict[str, Any]:
        """
        Instantly returns host static hardware specifications in <5ms.
        Cached permanently during the process lifetime.
        """
        if cls._cached_static_specs:
            return cls._cached_static_specs

        import platform
        hostname = platform.node() or "Worker-Node"
        os_platform = f"{platform.system()} {platform.release()} ({platform.machine()})"
        cpu_model = cls.get_cpu_model_name()
        cpu_cores = psutil.cpu_count(logical=True) or 1
        vm = psutil.virtual_memory()
        ram_total_gb = round(vm.total / (1024 ** 3), 2)
        ip = cls.get_primary_ip()

        cls._cached_static_specs = {
            "hostname": hostname,
            "os_platform": os_platform,
            "cpu_model": cpu_model,
            "cpu_cores": cpu_cores,
            "ram_total_gb": ram_total_gb,
            "primary_ip": ip
        }
        return cls._cached_static_specs

    @classmethod
    def get_cpu_model_name(cls) -> str:
        if cls._cached_cpu_name:
            return cls._cached_cpu_name
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            cpu_name, _ = winreg.QueryValueEx(key, "ProcessorNameString")
            cls._cached_cpu_name = cpu_name.strip()
            return cls._cached_cpu_name
        except Exception:
            import platform
            cls._cached_cpu_name = platform.processor() or "Generic x86_64 CPU"
            return cls._cached_cpu_name

    @classmethod
    def get_hardware_telemetry(cls, storage_path: str = ".") -> dict:
        static = cls.get_static_specs()

        # 1. CPU live load
        cpu_percent = psutil.cpu_percent(interval=None)

        # 2. RAM live load
        vm = psutil.virtual_memory()
        ram_used_gb = round((vm.total - vm.available) / (1024 ** 3), 2)
        ram_percent = vm.percent

        # 3. Disk
        try:
            usage = shutil.disk_usage(storage_path)
            disk_total = usage.total
            disk_free = usage.free
        except Exception:
            disk_total = 0
            disk_free = 0

        # 4. GPU via shared cached query
        gpu_info = cls.get_detailed_gpu_info()

        return {
            "hostname": static["hostname"],
            "os_platform": static["os_platform"],
            "cpu_model": static["cpu_model"],
            "cpu_cores": static["cpu_cores"],
            "cpu_percent": cpu_percent,
            "ram_total_gb": static["ram_total_gb"],
            "ram_used_gb": ram_used_gb,
            "ram_percent": ram_percent,
            "disk_total_bytes": disk_total,
            "disk_free_bytes": disk_free,
            "gpu_detected": gpu_info.get("gpu_detected", False),
            "gpu_name": gpu_info.get("name"),
            "gpu_vram_total_mb": gpu_info.get("vram_total_mb"),
            "gpu_vram_used_mb": gpu_info.get("vram_used_mb"),
            "gpu_util_percent": gpu_info.get("gpu_util_percent"),
            "temperature_c": gpu_info.get("temperature_c"),
            "mem_clock_mhz": gpu_info.get("mem_clock_mhz")
        }

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
                timeout=3,
                creationflags=CREATE_NO_WINDOW
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

    @staticmethod
    def get_primary_ip() -> str:
        """
        Determines the system's actual local IPv4 LAN address (e.g. 192.168.x.x, 10.x.x.x).
        Excludes 127.0.0.1 and APIPA auto-configuration (169.254.x.x).
        """
        # 1. UDP routing probe
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            if ip and not ip.startswith("127.") and not ip.startswith("169.254."):
                return ip
        except Exception:
            pass

        # 2. Iterate network adapters via psutil
        try:
            for iface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        ip = addr.address
                        if not ip.startswith("127.") and not ip.startswith("169.254."):
                            return ip
        except Exception:
            pass

        return "127.0.0.1"

    @staticmethod
    def get_all_lan_ips() -> List[str]:
        """
        Returns all valid IPv4 LAN addresses on the machine.
        """
        ips = []
        try:
            for iface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        ip = addr.address
                        if not ip.startswith("127.") and not ip.startswith("169.254."):
                            if ip not in ips:
                                ips.append(ip)
        except Exception:
            pass
        return ips or ["127.0.0.1"]

    @classmethod
    def get_detailed_gpu_info(cls) -> Dict[str, Any]:
        """
        Queries nvidia-smi for driver version, temperature, memory clock, and utilization.
        Returns empty/None fields if no NVIDIA GPU is detected. Zero fake data.
        """
        now_t = time.time()
        if cls._cached_gpu_telemetry:
            cached_t, cached_data = cls._cached_gpu_telemetry
            if (now_t - cached_t) < 0.8:
                return cached_data

        nvidia_smi = shutil.which("nvidia-smi")
        if not nvidia_smi:
            res_data = {"gpu_detected": False}
            cls._cached_gpu_telemetry = (now_t, res_data)
            return res_data

        try:
            res = subprocess.run(
                [
                    nvidia_smi,
                    "--query-gpu=name,driver_version,memory.total,memory.used,utilization.gpu,temperature.gpu,clocks.current.memory",
                    "--format=csv,noheader,nounits"
                ],
                capture_output=True,
                text=True,
                timeout=2,
                creationflags=CREATE_NO_WINDOW
            )
            if res.returncode == 0 and res.stdout.strip():
                line = res.stdout.strip().splitlines()[0]
                parts = [p.strip() for p in line.split(",")]
                res_data = {
                    "gpu_detected": True,
                    "name": parts[0] if len(parts) > 0 else "NVIDIA GPU",
                    "driver_version": parts[1] if len(parts) > 1 else "Unknown",
                    "vram_total_mb": int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0,
                    "vram_used_mb": int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0,
                    "gpu_util_percent": float(parts[4]) if len(parts) > 4 and parts[4].replace(".", "", 1).isdigit() else 0.0,
                    "temperature_c": int(parts[5]) if len(parts) > 5 and parts[5].isdigit() else None,
                    "mem_clock_mhz": int(parts[6]) if len(parts) > 6 and parts[6].isdigit() else None,
                }
                cls._cached_gpu_telemetry = (now_t, res_data)
                return res_data
        except Exception:
            pass

        res_data = {"gpu_detected": False}
        cls._cached_gpu_telemetry = (now_t, res_data)
        return res_data

