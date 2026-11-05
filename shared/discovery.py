"""
Universal Direct Ethernet Cable & LAN Auto-Discovery Service
Prioritizes high-speed direct PC-to-PC Ethernet cables (APIPA 169.254.x.x)
and local wired LAN networks without requiring any Wi-Fi or router DHCP.
"""

import socket
import json
import threading
import time
import subprocess
import ctypes
import sys
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

DISCOVERY_PORT = 8002
DISCOVERY_MAGIC_REQ = b"GPU_RENDER_DISCOVER_REQ_V1"
DISCOVERY_MAGIC_RESP_PREFIX = "GPU_RENDER_DISCOVER_RESP_V1:"

def get_active_adapters() -> List[Dict[str, Any]]:
    """
    Finds all physically active (is_up == True) non-loopback network adapters.
    Distinguishes direct Ethernet cables (APIPA 169.254.x.x), wired LAN, and Wi-Fi.
    Strictly excludes disconnected, virtual, and loopback adapters.
    """
    adapters = []
    try:
        import psutil
        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()

        for iface, if_addrs in addrs.items():
            st = stats.get(iface)
            if not st or not st.isup:
                continue

            name_low = iface.lower()
            # Ignore virtual, loopback, cellular, and WSL interfaces
            if any(k in name_low for k in [
                "loopback", "pseudo", "virtual", "vethernet", "vmware",
                "wsl", "bluetooth", "cellular", "tap", "tun"
            ]):
                continue

            is_eth = any(w in name_low for w in ["ethernet", "lan", "eth", "wired", "gigabit", "realtek", "intel"])
            is_wifi = any(w in name_low for w in ["wi-fi", "wifi", "wireless", "wlan", "802.11"])

            for a in if_addrs:
                if a.family == socket.AF_INET:
                    ip = a.address
                    if ip.startswith(("127.", "0.")):
                        continue

                    is_cable = ip.startswith("169.254.")
                    if is_cable:
                        ad_type = "Direct Ethernet Cable (APIPA)"
                    elif is_eth and not is_wifi:
                        ad_type = "Ethernet LAN (Wired)"
                    else:
                        ad_type = "Wi-Fi (Wireless LAN)"

                    adapters.append({
                        "interface": iface,
                        "ip": ip,
                        "is_up": True,
                        "is_ethernet": (is_eth or is_cable) and not is_wifi,
                        "is_cable": is_cable,
                        "type": ad_type
                    })
    except Exception:
        pass
    return adapters

def get_ethernet_ip() -> Optional[str]:
    """
    Finds the active physical wired Ethernet / LAN IPv4 address.
    Detects direct PC-to-PC Ethernet cables (APIPA 169.254.x.x) as well as router-assigned IPs.
    Strictly requires the interface to be active (is_up == True).
    """
    adapters = get_active_adapters()
    # 1. Prefer direct cable (169.254.x.x) on wired Ethernet
    for ad in adapters:
        if ad["is_cable"] and ad["is_ethernet"]:
            return ad["ip"]
    # 2. Any direct cable (169.254.x.x)
    for ad in adapters:
        if ad["is_cable"]:
            return ad["ip"]
    # 3. Any active wired Ethernet
    for ad in adapters:
        if ad["is_ethernet"]:
            return ad["ip"]
    return None

def get_all_lan_ips() -> List[str]:
    """Finds all valid, active, non-loopback IPv4 addresses on this PC (prioritizing Ethernet cable, then Wi-Fi)."""
    adapters = get_active_adapters()
    def sort_key(ad):
        if ad["is_cable"] and ad["is_ethernet"]:
            return 0
        if ad["is_ethernet"]:
            return 1
        if ad["is_cable"]:
            return 2
        return 3
    adapters.sort(key=sort_key)
    ips = [ad["ip"] for ad in adapters]

    if not ips:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                if not ip.startswith("127."):
                    ips.append(ip)
        except Exception:
            pass

    return ips or ["127.0.0.1"]

def get_local_ip() -> str:
    """Returns the primary active Ethernet / LAN IPv4 address (Ethernet cable is top priority, fallback Wi-Fi)."""
    eth_ip = get_ethernet_ip()
    if eth_ip:
        return eth_ip
    ips = get_all_lan_ips()
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
    and port 8002 (UDP Discovery) across all network profiles (Public, Private, Domain).
    Also removes any conflicting 'Block' rules that prevent Ethernet cable connections.
    """
    if sys.platform != "win32":
        return True

    flags = 0x08000000 if hasattr(subprocess, "CREATE_NO_WINDOW") else 0

    if is_admin():
        try:
            # 1. Delete blocking rules
            subprocess.run(["netsh", "advfirewall", "firewall", "delete", "rule", "name=gpuworkerserver.exe"], capture_output=True, creationflags=flags)
            subprocess.run(["netsh", "advfirewall", "firewall", "delete", "rule", "name=gpu_server_studio"], capture_output=True, creationflags=flags)
            subprocess.run(["netsh", "advfirewall", "firewall", "delete", "rule", "name=GPUWorkerServer"], capture_output=True, creationflags=flags)
            subprocess.run(["netsh", "advfirewall", "firewall", "delete", "rule", "name=GPUWorkerServer_TCP"], capture_output=True, creationflags=flags)
            subprocess.run(["netsh", "advfirewall", "firewall", "delete", "rule", "name=GPUWorkerServer_UDP"], capture_output=True, creationflags=flags)

            # 2. Add TCP port 8000 allow on ALL profiles (Public profile is used by direct Ethernet cable)
            subprocess.run(
                ["netsh", "advfirewall", "firewall", "add", "rule", "name=GPUWorkerServer_TCP", "dir=in", "action=allow", "protocol=TCP", f"localport={port}", "profile=any"],
                capture_output=True, creationflags=flags
            )
            # 3. Add UDP port 8002 allow on ALL profiles for discovery
            subprocess.run(
                ["netsh", "advfirewall", "firewall", "add", "rule", "name=GPUWorkerServer_UDP", "dir=in", "action=allow", "protocol=UDP", f"localport={DISCOVERY_PORT}", "profile=any"],
                capture_output=True, creationflags=flags
            )
            # 4. Allow ICMPv4 Ping
            subprocess.run(
                ["netsh", "advfirewall", "firewall", "add", "rule", "name=GPUWorkerServer_ICMP", "dir=in", "action=allow", "protocol=icmpv4:8,any", "profile=any"],
                capture_output=True, creationflags=flags
            )
            return True
        except Exception:
            return False
    else:
        # Request elevation once to permanently add the firewall rules
        try:
            cmd = (
                f'/c netsh advfirewall firewall delete rule name="gpuworkerserver.exe" & '
                f'netsh advfirewall firewall add rule name="GPUWorkerServer_TCP" dir=in action=allow protocol=TCP localport={port} profile=any & '
                f'netsh advfirewall firewall add rule name="GPUWorkerServer_UDP" dir=in action=allow protocol=UDP localport={DISCOVERY_PORT} profile=any & '
                f'netsh advfirewall firewall add rule name="GPUWorkerServer_ICMP" dir=in action=allow protocol=icmpv4:8,any profile=any'
            )
            ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", cmd, None, 0)
            return True
        except Exception:
            return False

class DiscoveryServer:
    """Runs in background on Worker Server to respond to client discovery requests over Ethernet cable / LAN."""
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
    """Client utility to scan and auto-discover running GPUWorkerServers over direct Ethernet cable or LAN."""

    @staticmethod
    def _warmup_arp(timeout: float = 0.2):
        """Sends quick ping requests to broadcast addresses to ensure ARP tables are populated on Windows."""
        try:
            flags = 0x08000000 if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
            # Ping direct cable APIPA broadcast and standard broadcast in background
            subprocess.Popen(["ping", "-n", "1", "-w", "200", "169.254.255.255"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=flags)
            subprocess.Popen(["ping", "-n", "1", "-w", "200", "255.255.255.255"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=flags)
            time.sleep(timeout)
        except Exception:
            pass

    @classmethod
    def discover_via_arp(cls, port: int = 8000, timeout: float = 0.5) -> List[Dict[str, Any]]:
        """
        Instantly locates the peer PC connected via direct Ethernet cable or LAN switch by checking the ARP table.
        Fastest and most reliable method for PC-to-PC direct cable connections.
        """
        found = []
        try:
            import httpx
            flags = 0x08000000 if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
            cls._warmup_arp(timeout=0.15)

            out = subprocess.check_output("arp -a", text=True, stderr=subprocess.DEVNULL, creationflags=flags)
            candidates = re.findall(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", out)
            my_ips = set(get_all_lan_ips())

            valid_targets = []
            for ip in set(candidates):
                if ip in my_ips or ip.startswith(("127.", "224.", "239.", "255.", "0.")):
                    continue
                if ip.endswith((".255", ".0")):
                    continue
                valid_targets.append(ip)

            # Prioritize direct Ethernet cable APIPA addresses (169.254.x.x)
            valid_targets.sort(key=lambda x: 0 if x.startswith("169.254.") else 1)

            def test_target(ip: str) -> Optional[Dict[str, Any]]:
                try:
                    with httpx.Client(timeout=timeout) as client:
                        r = client.get(f"http://{ip}:{port}/api/v1/ping")
                        if r.status_code == 200:
                            return {
                                "service": "GPUWorkerServer",
                                "ip": ip,
                                "port": port,
                                "hostname": ip
                            }
                except Exception:
                    pass
                return None

            with ThreadPoolExecutor(max_workers=15) as ex:
                futures = [ex.submit(test_target, ip) for ip in valid_targets]
                for f in as_completed(futures):
                    res = f.result()
                    if res:
                        found.append(res)
        except Exception:
            pass
        return found

    @staticmethod
    def discover_via_broadcast(timeout: float = 0.9) -> List[Dict[str, Any]]:
        """
        Sends UDP broadcast over each active physical interface (Ethernet cable and Wi-Fi).
        Binding to each adapter guarantees the broadcast packet physically exits through the direct cable.
        """
        found = []
        try:
            adapters = get_active_adapters()
            sockets = []

            # Create and bind dedicated UDP socket for EACH active adapter
            for ad in adapters:
                my_ip = ad.get("ip")
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind((my_ip, 0)) # Explicitly bound to this physical adapter
                    s.settimeout(timeout)
                    sockets.append((s, my_ip, ad.get("is_cable", False)))
                except Exception:
                    pass

            # Fallback unbound socket if no bound socket succeeded
            if not sockets:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    s.settimeout(timeout)
                    sockets.append((s, "0.0.0.0", False))
                except Exception:
                    pass

            # Send broadcast requests
            for s, my_ip, is_cable in sockets:
                b_targets = ["255.255.255.255"]
                if is_cable or my_ip.startswith("169.254."):
                    b_targets.append("169.254.255.255")
                elif "." in my_ip and not my_ip.startswith("0."):
                    pfx = my_ip.rsplit(".", 1)[0]
                    b_targets.append(f"{pfx}.255")

                for target in set(b_targets):
                    try:
                        s.sendto(DISCOVERY_MAGIC_REQ, (target, DISCOVERY_PORT))
                    except Exception:
                        pass

            start_t = time.time()
            seen_ips = set()
            while time.time() - start_t < timeout:
                for s, _, _ in sockets:
                    try:
                        data, addr = s.recvfrom(2048)
                        txt = data.decode("utf-8", errors="ignore")
                        if txt.startswith(DISCOVERY_MAGIC_RESP_PREFIX):
                            raw_json = txt[len(DISCOVERY_MAGIC_RESP_PREFIX):]
                            info = json.loads(raw_json)
                            server_ip = addr[0]
                            info["ip"] = server_ip
                            if server_ip not in seen_ips:
                                seen_ips.add(server_ip)
                                found.append(info)
                    except (socket.timeout, BlockingIOError):
                        continue
                    except Exception:
                        pass

            for s, _, _ in sockets:
                try:
                    s.close()
                except Exception:
                    pass
        except Exception:
            pass
        return found

    @staticmethod
    def discover_via_subnet_scan(port: int = 8000, max_scan_threads: int = 60, timeout: float = 0.3) -> List[Dict[str, Any]]:
        """Fast parallel subnet scan fallback for standard /24 LAN networks."""
        lan_ips = get_all_lan_ips()
        prefixes = set()
        for lip in lan_ips:
            if "." in lip and not lip.startswith(("127.", "169.254.")):
                prefixes.add(lip.rsplit(".", 1)[0])

        if not prefixes:
            return []

        targets = []
        for pfx in prefixes:
            targets.extend([f"{pfx}.{i}" for i in range(1, 255)])

        open_ips = []
        def check_host(ip: str) -> Optional[str]:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(timeout)
                    if s.connect_ex((ip, port)) == 0:
                        return ip
            except Exception:
                pass
            return None

        with ThreadPoolExecutor(max_workers=max_scan_threads) as executor:
            futures = [executor.submit(check_host, ip) for ip in targets]
            for fut in as_completed(futures):
                res = fut.result()
                if res:
                    open_ips.append(res)

        found = []
        for o_ip in open_ips:
            try:
                import httpx
                with httpx.Client(timeout=0.6) as client:
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
        """
        Runs ARP detection and multi-interface UDP broadcast concurrently.
        Instantly discovers direct Ethernet cable peers and LAN servers in <0.8s.
        """
        results = []
        seen = set()

        with ThreadPoolExecutor(max_workers=2) as ex:
            f_arp = ex.submit(cls.discover_via_arp, 8000, 0.45)
            f_bcast = ex.submit(cls.discover_via_broadcast, 0.75)

            for f in [f_arp, f_bcast]:
                try:
                    for s in f.result():
                        ip = s.get("ip")
                        if ip and ip not in seen:
                            seen.add(ip)
                            results.append(s)
                except Exception:
                    pass

        if results:
            return results

        # Fallback to standard subnet scan if neither ARP nor broadcast found anything
        return cls.discover_via_subnet_scan(port=8000, timeout=0.3)
