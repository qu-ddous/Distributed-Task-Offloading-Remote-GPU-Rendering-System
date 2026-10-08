import os
import json
import time
import asyncio
import hashlib
from pathlib import Path
from typing import Callable, Optional, Dict, Any
import httpx
import websockets
from shared.schemas import PROTOCOL_VERSION

class NetworkClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 8000, api_token: str = ""):
        self.host = host.strip()
        self.port = int(port)
        self.api_token = api_token.strip()
        self.base_url = f"http://{self.host}:{self.port}"
        self.ws_url = f"ws://{self.host}:{self.port}"

    def get_headers(self) -> Dict[str, str]:
        headers = {}
        if self.api_token:
            headers["X-API-Token"] = self.api_token
        return headers

    def ping_and_health(self, timeout: float = 3.0) -> Dict[str, Any]:
        """
        Synchronous ping & health check executed from a background thread.
        Returns dict with status, latency_ms, health_info or error.
        """
        start_time = time.time()
        try:
            with httpx.Client(timeout=timeout) as client:
                # 1. Ping
                ping_resp = client.get(f"{self.base_url}/api/v1/ping")
                latency_ms = round((time.time() - start_time) * 1000, 1)
                if ping_resp.status_code != 200:
                    return {
                        "success": False,
                        "error": f"Server ping failed with status code {ping_resp.status_code}."
                    }

                # 2. Health
                health_resp = client.get(f"{self.base_url}/api/v1/health", headers=self.get_headers())
                if health_resp.status_code == 401:
                    return {
                        "success": False,
                        "error": "Authentication failed (401 Unauthorized). Check API Token."
                    }
                elif health_resp.status_code != 200:
                    return {
                        "success": False,
                        "error": f"Health check returned error HTTP {health_resp.status_code}."
                    }

                health_data = health_resp.json()
                # Check version compatibility
                server_proto = health_data.get("protocol_version", "")
                if server_proto.split(".")[0] != PROTOCOL_VERSION.split(".")[0]:
                    return {
                        "success": False,
                        "error": f"Incompatible protocol: Client is {PROTOCOL_VERSION}, Server is {server_proto}."
                    }

                return {
                    "success": True,
                    "latency_ms": latency_ms,
                    "data": health_data
                }
        except httpx.ConnectError:
            return {
                "success": False,
                "error": f"Could not connect to {self.base_url}. Verify worker IP, port, and firewall."
            }
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": f"Connection to {self.base_url} timed out (4s limit)."
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}"
            }

    def compute_sha256(self, file_path: Path, progress_callback: Optional[Callable[[float], None]] = None) -> str:
        """
        Computes SHA-256 for a local file with optional progress updates (0.0 to 1.0).
        """
        hasher = hashlib.sha256()
        total_size = file_path.stat().st_size
        read_so_far = 0
        chunk_size = 2 * 1024 * 1024 # 2MB

        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
                read_so_far += len(chunk)
                if progress_callback and total_size > 0:
                    progress_callback(read_so_far / total_size)

        return hasher.hexdigest()

    def submit_job(
        self,
        input_file: Path,
        checksum: str,
        resolution: str,
        bitrate: str,
        preset: str,
        output_filename: str,
        allow_cpu_fallback: bool,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Uploads input file and job settings via streaming multipart/form-data.
        """
        url = f"{self.base_url}/api/v1/jobs"
        total_size = input_file.stat().st_size

        class ProgressFileReader:
            def __init__(self, path: Path, callback: Optional[Callable[[int, int], None]]):
                self.file = open(path, "rb")
                self.callback = callback
                self.uploaded = 0
                self.total = total_size

            def read(self, chunk_size=-1):
                chunk = self.file.read(chunk_size if chunk_size > 0 else 64 * 1024)
                if chunk:
                    self.uploaded += len(chunk)
                    if self.callback:
                        self.callback(self.uploaded, self.total)
                return chunk

            def close(self):
                self.file.close()

        reader = ProgressFileReader(input_file, progress_callback)
        try:
            files = {
                "file": (input_file.name, reader, "application/octet-stream")
            }
            data = {
                "checksum": checksum,
                "resolution": resolution,
                "bitrate": bitrate,
                "preset": preset,
                "output_filename": output_filename,
                "allow_cpu_fallback": "true" if allow_cpu_fallback else "false"
            }

            with httpx.Client(timeout=300.0) as client:
                resp = client.post(url, headers=self.get_headers(), data=data, files=files)
                reader.close()

                if resp.status_code == 201:
                    return {"success": True, "job": resp.json()}
                elif resp.status_code == 400:
                    return {"success": False, "error": f"Validation/Integrity error: {resp.json().get('detail')}"}
                elif resp.status_code == 413:
                    return {"success": False, "error": "File size exceeds server upload limit."}
                elif resp.status_code == 401:
                    return {"success": False, "error": "Unauthorized: Invalid API Token."}
                else:
                    return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text}"}
        except Exception as e:
            reader.close()
            return {"success": False, "error": f"Upload failed: {str(e)}"}

    def download_output_file(
        self,
        job_id: str,
        target_path: Path,
        expected_checksum: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Streams rendered video download and validates SHA-256 integrity.
        """
        url = f"{self.base_url}/api/v1/jobs/{job_id}/download"
        try:
            with httpx.Client(timeout=300.0) as client:
                with client.stream("GET", url, headers=self.get_headers()) as resp:
                    if resp.status_code != 200:
                        return {"success": False, "error": f"Download failed with HTTP {resp.status_code}"}

                    total_bytes = int(resp.headers.get("Content-Length", 0))
                    server_header_checksum = resp.headers.get("X-Checksum-SHA256")
                    downloaded_bytes = 0
                    hasher = hashlib.sha256()

                    with open(target_path, "wb") as f:
                        for chunk in resp.iter_bytes(chunk_size=1024 * 1024):
                            f.write(chunk)
                            hasher.update(chunk)
                            downloaded_bytes += len(chunk)
                            if progress_callback and total_bytes > 0:
                                progress_callback(downloaded_bytes, total_bytes)

                    download_hash = hasher.hexdigest().lower()
                    target_hash = expected_checksum or server_header_checksum
                    if target_hash and download_hash != target_hash.strip().lower():
                        return {
                            "success": False,
                            "error": f"Downloaded file checksum mismatch! (Server: {target_hash}, Local: {download_hash})"
                        }

                    return {
                        "success": True,
                        "file_path": str(target_path),
                        "bytes": downloaded_bytes,
                        "checksum": download_hash
                    }
        except Exception as e:
            if target_path.exists():
                target_path.unlink(missing_ok=True)
            return {"success": False, "error": f"Download interrupted: {str(e)}"}

    def cancel_job(self, job_id: str) -> bool:
        url = f"{self.base_url}/api/v1/jobs/{job_id}/cancel"
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.post(url, headers=self.get_headers())
                return resp.status_code == 200
        except Exception:
            return False

    async def listen_websocket(
        self,
        job_id: str,
        on_message: Callable[[Dict[str, Any]], None],
        stop_event: asyncio.Event
    ):
        """
        Connects to job's WebSocket stream and invokes on_message callback.
        """
        token_param = f"?token={self.api_token}" if self.api_token else ""
        uri = f"{self.ws_url}/api/v1/ws/{job_id}{token_param}"

        try:
            async with websockets.connect(uri) as ws:
                while not stop_event.is_set():
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=2.0)
                        data = json.loads(msg)
                        on_message(data)
                        if data.get("type") in ["state", "error"] and data.get("status") in ["completed", "failed", "cancelled"]:
                            break
                    except asyncio.TimeoutError:
                        continue
        except Exception as e:
            on_message({
                "type": "error",
                "message": f"WebSocket connection closed or unavailable: {str(e)}"
            })
