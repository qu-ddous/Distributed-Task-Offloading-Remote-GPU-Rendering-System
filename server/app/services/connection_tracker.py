import time
import threading
from typing import Dict, List, Any

class ClientConnectionTracker:
    """
    Real-time, thread-safe tracker for client connections, IP addresses,
    request counts, and transferred bytes.
    Zero mock/dummy data.
    """
    def __init__(self):
        self._lock = threading.Lock()
        # Key: ip_str -> dict
        self._connections: Dict[str, Dict[str, Any]] = {}
        self._total_bytes_transferred = 0

    def record_request(self, client_ip: str, client_port: int, bytes_count: int = 0):
        if not client_ip:
            return
        # Normalize loopback
        clean_ip = "127.0.0.1" if client_ip in ("127.0.0.1", "::1", "localhost") else client_ip
        now = time.time()

        with self._lock:
            self._total_bytes_transferred += max(0, bytes_count)
            if clean_ip not in self._connections:
                self._connections[clean_ip] = {
                    "ip": clean_ip,
                    "port": client_port or 0,
                    "first_seen": now,
                    "last_seen": now,
                    "requests_count": 1,
                    "bytes_transferred": bytes_count
                }
            else:
                conn = self._connections[clean_ip]
                conn["port"] = client_port or conn["port"]
                conn["last_seen"] = now
                conn["requests_count"] += 1
                conn["bytes_transferred"] += bytes_count

    def get_active_clients_count(self, timeout_sec: float = 5.0) -> int:
        now = time.time()
        with self._lock:
            return sum(1 for c in self._connections.values() if (now - c["last_seen"]) <= timeout_sec)

    def get_total_transferred_bytes(self) -> int:
        with self._lock:
            return self._total_bytes_transferred

    def get_connections_list(self) -> List[Dict[str, Any]]:
        now = time.time()
        with self._lock:
            result = []
            for c in self._connections.values():
                is_active = (now - c["last_seen"]) <= 5.0
                result.append({
                    "ip": c["ip"],
                    "port": c["port"],
                    "first_seen": c["first_seen"],
                    "last_seen": c["last_seen"],
                    "is_active": is_active,
                    "requests_count": c["requests_count"],
                    "bytes_transferred": c["bytes_transferred"]
                })
            # Sort by last seen descending
            result.sort(key=lambda x: x["last_seen"], reverse=True)
            return result

    def clear(self):
        with self._lock:
            self._connections.clear()
            self._total_bytes_transferred = 0

connection_tracker = ClientConnectionTracker()

