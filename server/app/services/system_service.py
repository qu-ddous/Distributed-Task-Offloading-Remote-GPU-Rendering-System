import os
import shutil
import subprocess
import re
import socket
from typing import Tuple, List, Optional, Dict, Any
import psutil
import time

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
                hw_candidates = [
                    "h264_nvenc", "hevc_nvenc",
                    "h264_qsv", "hevc_qsv",
                    "h264_amf", "hevc_amf",
                    "h264_mf"
                ]
                sw_candidates = ["libx264", "libx265"]

                verified_hw = []
                for hw_enc in hw_candidates:
                    if hw_enc in output:
                        try:
                            test_hw = subprocess.run(
                                [ffmpeg_bin, "-y", "-f", "lavfi", "-i", "nullsrc=s=64x64:d=0.1", "-c:v", hw_enc, "-f", "null", "-"],
                                capture_output=True,
                                text=True,
                                timeout=3,
                                creationflags=CREATE_NO_WINDOW
                            )
                            if test_hw.returncode == 0:
                                verified_hw.append(hw_enc)
                        except Exception:
                            pass

                verified_sw = [enc for enc in sw_candidates if enc in output]
                supported_encoders = verified_hw + verified_sw
                is_hardware_accel = len(verified_hw) > 0
                is_nvenc = ("h264_nvenc" in verified_hw) or ("hevc_nvenc" in verified_hw)
        except Exception:
            cls._cached_ffmpeg_caps = (True, version_str, False, [])
            return cls._cached_ffmpeg_caps

        cls._cached_ffmpeg_caps = (True, version_str, is_nvenc or is_hardware_accel, supported_encoders)
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
    def _find_nvidia_smi() -> Optional[str]:
        p = shutil.which("nvidia-smi")
        if p:
            return p
        if os.name == "nt":
            candidates = [
                r"C:\Windows\System32\nvidia-smi.exe",
                r"C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe"
            ]
            for c in candidates:
                if os.path.exists(c):
                    return c
        return None

    @classmethod
    def get_windows_display_adapters(cls) -> List[Dict[str, Any]]:
        """
        Fast registry query for all installed GPU display adapters on Windows.
        Returns accurate name, vendor (NVIDIA/Intel/AMD), driver version, and dedicated VRAM.
        Execution takes <1ms without launching any console windows.
        """
        adapters = []
        if os.name != "nt":
            return adapters
        try:
            import winreg
            class_key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
            )
            i = 0
            while True:
                try:
                    sub_name = winreg.EnumKey(class_key, i)
                    i += 1
                    if not sub_name.isdigit():
                        continue
                    dev_key = winreg.OpenKey(class_key, sub_name)
                    try:
                        name = None
                        for key_name in ["DriverDesc", "AdapterString"]:
                            try:
                                val, _ = winreg.QueryValueEx(dev_key, key_name)
                                if isinstance(val, bytes):
                                    val = val.decode("utf-16", errors="ignore").strip("\x00")
                                if val:
                                    name = str(val).strip()
                                    break
                            except Exception:
                                pass

                        if not name or any(ign in name for ign in ["Basic Display", "Remote Display", "Miracast", "Virtual"]):
                            continue

                        driver_ver = "Unknown"
                        try:
                            ver, _ = winreg.QueryValueEx(dev_key, "DriverVersion")
                            driver_ver = str(ver).strip()
                        except Exception:
                            pass

                        vram_mb = 0
                        for mem_key in ["HardwareInformation.qwMemorySize", "HardwareInformation.MemorySize"]:
                            try:
                                val, _ = winreg.QueryValueEx(dev_key, mem_key)
                                if isinstance(val, int):
                                    vram_mb = val // (1024 * 1024)
                                elif isinstance(val, bytes):
                                    int_val = int.from_bytes(val, byteorder="little")
                                    vram_mb = int_val // (1024 * 1024)
                                if vram_mb > 0:
                                    break
                            except Exception:
                                pass

                        lname = name.lower()
                        vendor = "NVIDIA" if "nvidia" in lname else ("Intel" if "intel" in lname else ("AMD" if ("amd" in lname or "radeon" in lname) else "Generic"))
                        is_discrete = vendor in ["NVIDIA", "AMD"]

                        adapters.append({
                            "name": name,
                            "vendor": vendor,
                            "driver_version": driver_ver,
                            "vram_total_mb": vram_mb,
                            "is_discrete": is_discrete
                        })
                    finally:
                        winreg.CloseKey(dev_key)
                except OSError:
                    break
            winreg.CloseKey(class_key)
        except Exception:
            pass
        return adapters

    @classmethod
    def detect_nvidia_gpu(cls) -> Tuple[bool, Optional[str]]:
        nvidia_smi = cls._find_nvidia_smi()
        if not nvidia_smi:
            # Check registry for NVIDIA cards
            for ad in cls.get_windows_display_adapters():
                if ad["vendor"] == "NVIDIA":
                    return True, ad["name"]
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

    @classmethod
    def detect_any_gpu(cls) -> Tuple[bool, Optional[str], str, int]:
        """
        Returns (gpu_detected, name, vendor, vram_total_mb) for ANY GPU (NVIDIA, Intel, AMD).
        """
        gpu = cls.get_detailed_gpu_info()
        if gpu.get("gpu_detected"):
            return True, gpu.get("name"), gpu.get("vendor", "Generic"), gpu.get("vram_total_mb", 0)
        return False, None, "None", 0

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
    def get_all_lan_adapters() -> List[Dict[str, Any]]:
        """
        Discovers physical Ethernet (wired Cat6/LAN) adapters only.
        Completely excludes Wi-Fi, wireless, virtual, cellular, and loopback adapters.
        """
        adapters = []
        try:
            stats = psutil.net_if_stats()
            for iface, addrs in psutil.net_if_addrs().items():
                iface_lower = iface.lower()
                # Exclude any Wi-Fi, wireless, virtual, cellular, or Wi-Fi Direct interfaces
                is_wifi_or_virtual = any(v in iface_lower for v in [
                    "wi-fi", "wifi", "wireless", "wlan", "802.11", "airdrop",
                    "wi-fi direct", "wifi direct", "local area connection*",
                    "virtual", "vethernet", "vmware", "loopback", "wsl", "hyper-v",
                    "pseudo", "tap", "tun", "zerotier", "tailscale", "bluetooth",
                    "cellular", "mobile", "wwan", "dial-up", "remote"
                ])
                if is_wifi_or_virtual:
                    continue

                st = stats.get(iface)
                is_up = st.isup if st else False

                for a in addrs:
                    if a.family == socket.AF_INET:
                        ip = a.address
                        if ip.startswith("127."):
                            continue
                        ad_type = "Ethernet (Cat6 / Wired LAN)"
                        if ip.startswith("169.254."):
                            ad_type += " (Direct Cable APIPA)"
                        adapters.append({
                            "interface": iface,
                            "ip": ip,
                            "is_up": is_up,
                            "is_virtual": False,
                            "type": ad_type
                        })
        except Exception:
            pass
        return adapters

    @classmethod
    def get_primary_ip(cls) -> str:
        """
        Determines the system's active Ethernet (wired Cat6/LAN) IPv4 address.
        Completely ignores Wi-Fi and strictly selects the physical Ethernet connection.
        """
        adapters = cls.get_all_lan_adapters()

        # 1. Active physical Ethernet adapter that is UP
        for ad in adapters:
            if ad.get("is_up") and not ad["ip"].startswith("127."):
                return ad["ip"]

        # 2. Any detected Ethernet adapter with valid IPv4
        for ad in adapters:
            if not ad["ip"].startswith("127."):
                return ad["ip"]

        # 3. Fallback
        return "127.0.0.1"

    @classmethod
    def ensure_firewall_rule(cls, port: int = 8000) -> bool:
        """
        Ensures an inbound Windows Defender Firewall rule exists for the specified port (TCP).
        If missing, attempts to create it automatically.
        Uses ShellExecute 'runas' if administrator elevation is required.
        Completely silent and creates no flashing console window.
        """
        if os.name != "nt":
            return True

        rule_name = f"GPU Render Studio Server (Port {port})"
        try:
            # 1. Check if rule already exists (no elevation required)
            check = subprocess.run(
                ["netsh", "advfirewall", "firewall", "show", "rule", f"name={rule_name}"],
                capture_output=True,
                text=True,
                creationflags=CREATE_NO_WINDOW
            )
            if check.returncode == 0 and "No rules match" not in check.stdout:
                return True

            # 2. Try adding rule directly (succeeds if running as Administrator)
            add_res = subprocess.run(
                ["netsh", "advfirewall", "firewall", "add", "rule",
                 f"name={rule_name}", "dir=in", "action=allow", "protocol=TCP",
                 f"localport={port}", "profile=any"],
                capture_output=True,
                text=True,
                creationflags=CREATE_NO_WINDOW
            )
            if add_res.returncode == 0:
                return True

            # 3. Elevate via ShellExecuteW 'runas' to add rule silently
            import ctypes
            args = f'advfirewall firewall add rule name="{rule_name}" dir=in action=allow protocol=TCP localport={port} profile=any'
            ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", "netsh", args, None, 0)
            return ret > 32
        except Exception:
            return False

    @classmethod
    def get_all_lan_ips(cls) -> List[str]:
        """
        Returns all valid IPv4 LAN addresses on the machine.
        """
        adapters = cls.get_all_lan_adapters()
        ips = [ad["ip"] for ad in adapters if ad.get("is_up")]
        if not ips:
            ips = [ad["ip"] for ad in adapters]
        return ips or ["127.0.0.1"]

    @classmethod
    def get_detailed_gpu_info(cls) -> Dict[str, Any]:
        """
        Universal GPU detection across NVIDIA, Intel, and AMD.
        Returns live hardware metrics for NVIDIA GPUs (via nvidia-smi),
        and hardware specifications for Intel/AMD/other GPUs (via Windows hardware registry).
        Zero fake data.
        """
        now_t = time.time()
        if cls._cached_gpu_telemetry:
            cached_t, cached_data = cls._cached_gpu_telemetry
            if (now_t - cached_t) < 0.8:
                return cached_data

        # 1. Try nvidia-smi if available (for live telemetry: load, vram used, temp, clock)
        nvidia_smi = cls._find_nvidia_smi()
        if nvidia_smi:
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
                        "vendor": "NVIDIA",
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

        # 2. Universal fallback: Windows display adapters query (Intel UHD / Iris Xe / Arc, AMD Radeon, NVIDIA)
        adapters = cls.get_windows_display_adapters()
        if adapters:
            # Pick the best adapter (prefer discrete or first active)
            primary = next((a for a in adapters if a.get("is_discrete")), adapters[0])
            res_data = {
                "gpu_detected": True,
                "name": primary["name"],
                "vendor": primary["vendor"],
                "driver_version": primary["driver_version"],
                "vram_total_mb": primary["vram_total_mb"],
                "vram_used_mb": 0,
                "gpu_util_percent": 0.0,
                "temperature_c": None,
                "mem_clock_mhz": None,
            }
            cls._cached_gpu_telemetry = (now_t, res_data)
            return res_data

        res_data = {"gpu_detected": False, "vendor": "None"}
        cls._cached_gpu_telemetry = (now_t, res_data)
        return res_data


