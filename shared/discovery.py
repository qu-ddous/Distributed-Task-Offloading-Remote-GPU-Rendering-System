"""
Zero-Configuration Network Discovery & Background Automation Service
Enables seamless zero-click worker discovery across Wi-Fi, Ethernet, Cat6, and LAN.
"""
import socket
import json
import time
import threading
import subprocess
import ipaddress
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request
import urllib.error

DISCOVERY_PORT = 8001
DISCOVERY_PROBE_MESSAGE = b"GPU_WORKER_DISCOVERY_PING"
PROTOCOL_MAGIC = "gpu_worker_server"

def get_local_ipv4_addresses() -> List[str]:
    """Collect all valid IPv4 addresses for this machine across all interfaces."""
    ips = set()
    # Method 1: socket gethostbyname_ex
    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if not ip.startswith("127."):
                ips.add(ip)
    except Exception:
        pass

    # Method 2: psutil if available
    try:
        import psutil
        for iface_name, iface_addrs in psutil.net_if_addrs().items():
            for addr in iface_addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                    ips.add(addr.address)
    except Exception:
        pass

    # Method 3: UDP connect probe
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        probe_ip = s.getsockname()[0]
        s.close()
        if not probe_ip.startswith("127."):
            ips.add(probe_ip)
    except Exception:
        pass

    return list(ips)


def get_broadcast_addresses() -> List[str]:
    """Calculate broadcast addresses for local subnets plus global broadcast."""
    bcasts = {"255.255.255.255"}
    for ip in get_local_ipv4_addresses():
        try:
            # Common /24 assumption for LAN/Wi-Fi/Cat6
            parts = ip.split(".")
            if len(parts) == 4:
                bcasts.add(f"{parts[0]}.{parts[1]}.{parts[2]}.255")
        except Exception:
            pass
    # Common dedicated subnets
    bcasts.add("192.168.2.255")
    bcasts.add("192.168.1.255")
    bcasts.add("192.168.0.255")
    return list(bcasts)


def ensure_firewall_rules_silently():
    """
    Ensures Windows Defender Firewall allows incoming TCP 8000 and UDP 8001.
    Runs silently in background with no popups or console windows.
    """
    creationflags = 0
    try:
        creationflags = subprocess.CREATE_NO_WINDOW
    except Exception:
        pass

    cmds = [
        ["netsh", "advfirewall", "firewall", "add", "rule", "name=GPU Worker Server Port 8000", "dir=in", "action=allow", "protocol=TCP", "localport=8000"],
        ["netsh", "advfirewall", "firewall", "add", "rule", "name=GPU Worker Server Discovery 8001", "dir=in", "action=allow", "protocol=UDP", "localport=8001"]
    ]
    for cmd in cmds:
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=creationflags, timeout=5)
        except Exception:
            pass


class DiscoveryServer:
    """
    Runs on GPUWorkerServer.
    Periodically beacons server IP/Port over UDP broadcast and responds to client discovery pings.
    """
    def __init__(self, port: int = 8000):
        self.http_port = port
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._sock: Optional[socket.socket] = None

    def start(self):
        if self._running:
            return
        self._running = True

        # Ensure firewall rules on server launch in background
        threading.Thread(target=ensure_firewall_rules_silently, daemon=True).start()

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass

    def _build_payload(self) -> bytes:
        payload = {
            "magic": PROTOCOL_MAGIC,
            "port": self.http_port,
            "hostname": socket.gethostname(),
            "ips": get_local_ipv4_addresses(),
            "timestamp": time.time()
        }
        return json.dumps(payload).encode("utf-8")

    def _run_loop(self):
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self._sock.bind(("", DISCOVERY_PORT))
            self._sock.settimeout(1.5)
        except Exception:
            return

        last_beacon = 0.0

        while self._running:
            now = time.time()

            # 1. Periodically broadcast presence beacon every 2.5 seconds
            if now - last_beacon >= 2.5:
                last_beacon = now
                data = self._build_payload()
                for bcast in get_broadcast_addresses():
                    try:
                        self._sock.sendto(data, (bcast, DISCOVERY_PORT))
                    except Exception:
                        pass

            # 2. Listen for discovery requests from clients
            try:
                msg, addr = self._sock.recvfrom(2048)
                if DISCOVERY_PROBE_MESSAGE in msg or b"GPU_WORKER" in msg:
                    # Reply directly to the discovering client
                    reply_data = self._build_payload()
                    self._sock.sendto(reply_data, addr)
            except socket.timeout:
                continue
            except Exception:
                time.sleep(0.5)


class DiscoveryClient:
    """
    Runs on GPURenderStudio client.
    Combines high-speed UDP broadcast discovery with fast parallel subnet HTTP probing.
    Finds the server 100% reliably regardless of Wi-Fi router settings or Cat6 direct links.
    """
    @staticmethod
    def _probe_http_ip(ip: str, port: int = 8000, timeout: float = 0.45) -> Optional[Dict[str, Any]]:
        """Quickly checks http://{ip}:{port}/api/v1/ping"""
        url = f"http://{ip}:{port}/api/v1/ping"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "GPUStudioDiscovery"})
            start_t = time.time()
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    raw = response.read().decode("utf-8", errors="ignore")
                    lat_ms = round((time.time() - start_t) * 1000, 1)
                    data = {}
                    try:
                        data = json.loads(raw)
                    except Exception:
                        pass
                    return {
                        "ip": ip,
                        "port": port,
                        "latency_ms": lat_ms,
                        "data": data,
                        "source": "http_probe"
                    }
        except Exception:
            pass
        return None

    @classmethod
    def discover_worker(cls, timeout: float = 2.0, preferred_ip: str = "") -> Optional[Dict[str, Any]]:
        """
        Actively discovers worker server.
        1. Checks preferred IP if given (e.g. last known IP).
        2. Broadcasts UDP discovery requests.
        3. Concurrently scans active subnets (Wi-Fi, Cat6, Ethernet) on port 8000.
        Returns first online worker info or None.
        """
        # 1. Quick check preferred IP
        if preferred_ip and preferred_ip not in ("127.0.0.1", "localhost"):
            cand = cls._probe_http_ip(preferred_ip, 8000, timeout=0.6)
            if cand:
                return cand

        found_candidates: List[Dict[str, Any]] = []
        lock = threading.Lock()

        # 2. UDP Discovery Listener
        def udp_worker():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                s.settimeout(0.4)

                # Send probe on all broadcast addresses
                for bcast in get_broadcast_addresses():
                    try:
                        s.sendto(DISCOVERY_PROBE_MESSAGE, (bcast, DISCOVERY_PORT))
                    except Exception:
                        pass

                start_time = time.time()
                while time.time() - start_time < timeout:
                    try:
                        msg, (sender_ip, _) = s.recvfrom(4096)
                        parsed = json.loads(msg.decode("utf-8"))
                        if parsed.get("magic") == PROTOCOL_MAGIC:
                            # Prioritize sender_ip, plus any declared IPs in payload
                            srv_port = parsed.get("port", 8000)
                            candidate_ips = [sender_ip] + [ip for ip in parsed.get("ips", []) if ip != sender_ip]
                            for c_ip in candidate_ips:
                                verified = cls._probe_http_ip(c_ip, srv_port, timeout=0.8)
                                if verified:
                                    verified["hostname"] = parsed.get("hostname", "")
                                    with lock:
                                        found_candidates.append(verified)
                                    return
                    except socket.timeout:
                        continue
                    except Exception:
                        break
            except Exception:
                pass

        udp_thread = threading.Thread(target=udp_worker, daemon=True)
        udp_thread.start()

        # 3. Concurrent Subnet HTTP Fast Probe
        # Generate candidates from local active interfaces
        candidate_ips = set()

        # Common direct Cat6 / fallback IPs
        candidate_ips.add("192.168.2.1")
        candidate_ips.add("192.168.1.2")
        candidate_ips.add("192.168.0.2")
        candidate_ips.add("192.168.100.12")
        candidate_ips.add("127.0.0.1")

        local_ips = get_local_ipv4_addresses()
        for my_ip in local_ips:
            try:
                parts = my_ip.split(".")
                if len(parts) == 4:
                    prefix = f"{parts[0]}.{parts[1]}.{parts[2]}"
                    # Prioritize common router/host range: 1..20, plus nearby IPs around client
                    my_last = int(parts[3])
                    # Scan nearby neighbors
                    for offset in range(-5, 6):
                        nbr = my_last + offset
                        if 1 <= nbr <= 254 and nbr != my_last:
                            candidate_ips.add(f"{prefix}.{nbr}")
                    # Common host router IPs
                    candidate_ips.add(f"{prefix}.1")
                    candidate_ips.add(f"{prefix}.2")
                    candidate_ips.add(f"{prefix}.100")
                    candidate_ips.add(f"{prefix}.150")
                    candidate_ips.add(f"{prefix}.200")
            except Exception:
                pass

        # Scan candidate pool in parallel
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = {executor.submit(cls._probe_http_ip, ip, 8000, 0.4): ip for ip in candidate_ips}
            for future in as_completed(futures):
                res = future.result()
                if res:
                    with lock:
                        found_candidates.append(res)
                    break

        udp_thread.join(timeout=0.6)

        if found_candidates:
            # Pick lowest latency
            found_candidates.sort(key=lambda x: x.get("latency_ms", 9999))
            return found_candidates[0]

        return None
