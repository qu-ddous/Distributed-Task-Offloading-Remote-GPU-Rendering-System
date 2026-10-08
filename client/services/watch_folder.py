"""
Watch Folder Automation Service
Enables seamless 3rd-party video editing integration (Adobe Premiere Pro,
DaVinci Resolve, Blender, After Effects, HandBrake, Filmora).
When any external editor exports a video into the watched folder,
this service automatically detects it, verifies file write completion,
and offloads the render job to the remote GPU worker node.
"""

import os
import time
import threading
from pathlib import Path
from typing import Callable, Optional, Set

from client.services.network_client import NetworkClient

SUPPORTED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".wmv", ".flv", ".ts"}

class WatchFolderService:
    def __init__(self, on_new_video_detected: Callable[[Path, str], None]):
        self.on_new_video_detected = on_new_video_detected
        self.watch_dir: Optional[Path] = None
        self._is_running = False
        self._thread: Optional[threading.Thread] = None
        self._processed_files: Set[str] = set()

    def set_watch_directory(self, directory: Path):
        self.watch_dir = Path(directory)
        self.watch_dir.mkdir(parents=True, exist_ok=True)

    def start(self):
        if self._is_running or not self.watch_dir:
            return
        self._is_running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._is_running = False

    def is_active(self) -> bool:
        return self._is_running

    def _monitor_loop(self):
        while self._is_running:
            try:
                if self.watch_dir and self.watch_dir.exists():
                    for file_path in self.watch_dir.iterdir():
                        if not self._is_running:
                            break
                        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                            file_key = f"{file_path.name}_{file_path.stat().st_mtime}"
                            if file_key in self._processed_files:
                                continue

                            # Verify that 3rd-party exporter has finished writing to file
                            if self._is_file_ready(file_path):
                                self._processed_files.add(file_key)
                                net = NetworkClient()
                                checksum = net.compute_sha256(file_path)
                                self.on_new_video_detected(file_path, checksum)
            except Exception:
                pass
            time.sleep(2.0)

    def _is_file_ready(self, file_path: Path) -> bool:
        """
        Polls file size to ensure the external exporter (Premiere, Blender, etc.)
        has completely finished saving the render file and closed the write lock.
        """
        try:
            initial_size = file_path.stat().st_size
            if initial_size == 0:
                return False
            time.sleep(1.2)
            final_size = file_path.stat().st_size
            if initial_size != final_size:
                return False

            # Check if file can be opened for reading exclusively
            with open(file_path, "rb") as f:
                f.read(1024)
            return True
        except (PermissionError, OSError):
            return False

