"""
Universal LAN Auto-Discovery & Zero-Config Networking Service
Enables any client PC to instantly discover and connect to any server PC
on the same local Wi-Fi / Ethernet LAN without manual IP configuration.
"""

import socket
import json
import threading
import time
import subprocess
import ctypes
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

DISCOVERY_PORT = 8002
DISCOVERY_MAGIC_REQ = b"GPU_RENDER_DISCOVER_REQ_V1"
DISCOVERY_MAGIC_RESP_PREFIX = "GPU_RENDER_DISCOVER_RESP_V1:"

def get_all_lan_ips() -> List[str]:
    """Finds all valid, active, non-loopback IPv4 addresses on this PC."""
    real_ips = []
    try:
        import psutil
        for iface, addrs in psutil.net_if_addrs().items():
            for a in addrs:
                if a.family == socket.AF_INET:
                    ip = a.address
                    if not ip.startswith(("127.", "169.254.", "0.")):
                        real_ips.append(ip)
    except Exception:
        pass

    if not real_ips:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                if not ip.startswith(("127.", "169.254.")):
                    real_ips.append(ip)
        except Exception:
            pass

    return real_ips or ["127.0.0.1"]

def get_local_ip() -> str:
    """Returns the primary LAN IPv4 address."""
    ips = get_all_lan_ips()
    for ip in ips:
        if ip.startswith(("192.168.", "10.", "172.")):
            return ip
    return ips[0]

def is_admin() -> bool:
    if sys.platform != "win32":
        return True
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def ensure_windows_firewall_allowed(port: int = 8000) -> bool:
    """
    Ensures Windows Firewall allows incoming connections on port 8000 (TCP)
    and port 8002 (UDP Discovery). If not elevated, requests UAC prompt once.
    """
    if sys.platform != "win32":
        return True

    rule_tcp = "GPUWorkerServer"
    rule_udp = "GPUWorkerServer_UDP"

    try:
        chk = subprocess.run(
            ["netsh", "advfirewall", "firewall", "show", "rule", f"name={rule_tcp}"],
            capture_output=True,
            creationflags=0x08000000 if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
        )
        if chk.returncode == 0 and b"GPUWorkerServer" in chk.stdout:
            return True
    except Exception:
        pass

    # If running with admin privileges, add rules directly
    if is_admin():
        try:
            subprocess.run(
                ["netsh", "advfirewall", "firewall", "add", "rule", f"name={rule_tcp}", "dir=in", "action=allow", "protocol=TCP", f"localport={port}"],
                capture_output=True,
                creationflags=0x08000000 if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
            )
            subprocess.run(
                ["netsh", "advfirewall", "firewall", "add", "rule", f"name={rule_udp}", "dir=in", "action=allow", "protocol=UDP", f"localport={DISCOVERY_PORT}"],
                capture_output=True,
                creationflags=0x08000000 if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
            )
            return True
        except Exception:
            return False
    else:
        # Request elevation once to permanently add the firewall rules
        try:
            cmd = f'/c netsh advfirewall firewall add rule name="{rule_tcp}" dir=in action=allow protocol=TCP localport={port} & netsh advfirewall firewall add rule name="{rule_udp}" dir=in action=allow protocol=UDP localport={DISCOVERY_PORT}'
            ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", cmd, None, 0)
            return True
        except Exception:
            return False

class DiscoveryServer:
    """Runs in background on Worker Server to respond to client discovery broadcasts."""
    def __init__(self, server_port: int = 8000):
        self.server_port = server_port
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.sock: Optional[socket.socket] = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass

    def _listen_loop(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                self.sock.bind(("", DISCOVERY_PORT))
            except Exception:
                return
            self.sock.settimeout(2.0)

            while self.running:
                try:
                    data, addr = self.sock.recvfrom(1024)
                    if data == DISCOVERY_MAGIC_REQ:
                        info = {
                            "service": "GPUWorkerServer",
                            "port": self.server_port,
                            "hostname": socket.gethostname(),
                            "ip": get_local_ip()
                        }
                        resp_msg = f"{DISCOVERY_MAGIC_RESP_PREFIX}{json.dumps(info)}".encode("utf-8")
                        self.sock.sendto(resp_msg, addr)
                except socket.timeout:
                    continue
                except Exception:
                    break
        except Exception:
            pass

class DiscoveryClient:
    """Client utility to scan and auto-discover running GPUWorkerServers on the LAN."""
    @staticmethod
    def discover_via_broadcast(timeout: float = 1.0) -> List[Dict[str, Any]]:
        found = []
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(timeout)

            broadcast_ips = ["255.255.255.255"]
            lan_ips = get_all_lan_ips()
            for lip in lan_ips:
                if "." in lip:
                    prefix = lip.rsplit(".", 1)[0]
                    broadcast_ips.append(f"{prefix}.255")

            for b_ip in set(broadcast_ips):
                try:
                    sock.sendto(DISCOVERY_MAGIC_REQ, (b_ip, DISCOVERY_PORT))
                except Exception:
                    pass

            start_t = time.time()
            seen_ips = set()
            while time.time() - start_t < timeout:
                try:
                    data, addr = sock.recvfrom(2048)
                    txt = data.decode("utf-8", errors="ignore")
                    if txt.startswith(DISCOVERY_MAGIC_RESP_PREFIX):
                        raw_json = txt[len(DISCOVERY_MAGIC_RESP_PREFIX):]
                        info = json.loads(raw_json)
                        server_ip = addr[0]
                        info["ip"] = server_ip
                        if server_ip not in seen_ips:
                            seen_ips.add(server_ip)
                            found.append(info)
                except socket.timeout:
                    break
                except Exception:
                    break
            sock.close()
        except Exception:
            pass
        return found

    @staticmethod
    def discover_via_subnet_scan(port: int = 8000, max_scan_threads: int = 60, timeout: float = 0.35) -> List[Dict[str, Any]]:
        """Fast parallel subnet scan fallback if router blocks UDP broadcast."""
        lan_ips = get_all_lan_ips()
        prefixes = set()
        for lip in lan_ips:
            if "." in lip and not lip.startswith("127."):
                prefixes.add(lip.rsplit(".", 1)[0])

        if not prefixes:
            return []

        targets = []
        for pfx in prefixes:
            targets.extend([f"{pfx}.{i}" for i in range(1, 255)])

        found = []

        def check_host(ip: str) -> Optional[str]:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(timeout)
                    if s.connect_ex((ip, port)) == 0:
                        return ip
            except Exception:
                pass
            return None

        open_ips = []
        with ThreadPoolExecutor(max_workers=max_scan_threads) as executor:
            futures = [executor.submit(check_host, ip) for ip in targets]
            for fut in as_completed(futures):
                res = fut.result()
                if res:
                    open_ips.append(res)

        for o_ip in open_ips:
            try:
                import httpx
                with httpx.Client(timeout=0.8) as client:
                    r = client.get(f"http://{o_ip}:{port}/api/v1/ping")
                    if r.status_code == 200:
                        found.append({
                            "service": "GPUWorkerServer",
                            "ip": o_ip,
                            "port": port,
                            "hostname": o_ip
                        })
            except Exception:
                pass

        return found

    @classmethod
    def auto_find_servers(cls) -> List[Dict[str, Any]]:
        """Tries UDP broadcast first (<1s), falls back to subnet scan (~0.6s)."""
        servers = cls.discover_via_broadcast(timeout=1.0)
        if servers:
            return servers
        return cls.discover_via_subnet_scan(port=8000, timeout=0.35)
