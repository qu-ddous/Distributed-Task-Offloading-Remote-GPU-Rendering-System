"""
Watch Folder Automation Service
Enables seamless 3rd-party video editing integration (CapCut, Adobe Premiere Pro,
DaVinci Resolve, Blender, After Effects, HandBrake, Filmora).
When any external editor exports a video into the watched folder (or any subfolder),
this service automatically detects it, verifies file write completion,
and offloads the render job to the remote GPU worker node.
"""

import os
import time
import threading
from pathlib import Path
from typing import Callable, Optional, Set

from client.services.network_client import NetworkClient

SUPPORTED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".wmv", ".flv", ".ts", ".webm", ".m4v"}

class WatchFolderService:
    def __init__(self, on_new_video_detected: Callable[[Path, str], None]):
        self.on_new_video_detected = on_new_video_detected
        self.watch_dir: Optional[Path] = None
        self._is_running = False
        self._thread: Optional[threading.Thread] = None
        self._processed_files: Set[str] = set()

    def set_watch_directory(self, directory: Path):
        self.watch_dir = Path(directory)
        try:
            self.watch_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    def start(self):
        if self._is_running or not self.watch_dir:
            return
        self._is_running = True
        self._pre_seed_existing_files()
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._is_running = False

    def is_active(self) -> bool:
        return self._is_running

    def _pre_seed_existing_files(self):
        """Pre-seeds existing files older than 60 seconds so old archive videos aren't re-rendered on launch."""
        if not self.watch_dir or not self.watch_dir.exists():
            return
        now = time.time()
        try:
            for root, _, filenames in os.walk(self.watch_dir):
                for fname in filenames:
                    fpath = Path(root) / fname
                    if fpath.suffix.lower() in SUPPORTED_EXTENSIONS:
                        try:
                            st = fpath.stat()
                            # If file was modified more than 60 seconds ago, consider it already known
                            if (now - st.st_mtime) > 60:
                                file_key = f"{fpath.resolve()}_{st.st_mtime}_{st.st_size}"
                                self._processed_files.add(file_key)
                        except OSError:
                            pass
        except Exception:
            pass

    def _monitor_loop(self):
        while self._is_running:
            try:
                if self.watch_dir and self.watch_dir.exists():
                    # Recursive scan through watch directory & any subdirectories (CapCut / Premiere project subfolders)
                    for root, _, filenames in os.walk(self.watch_dir):
                        if not self._is_running:
                            break
                        for fname in filenames:
                            fpath = Path(root) / fname
                            fname_lower = fname.lower()

                            # Skip hidden files, temp files, and downloaded remote render outputs
                            if (
                                fname_lower.startswith(".")
                                or fname_lower.endswith(".tmp")
                                or fname_lower.endswith(".crdownload")
                                or fname_lower.endswith(".part")
                                or "_remote_" in fname_lower
                            ):
                                continue

                            if fpath.suffix.lower() in SUPPORTED_EXTENSIONS:
                                try:
                                    st = fpath.stat()
                                    file_key = f"{fpath.resolve()}_{st.st_mtime}_{st.st_size}"
                                except OSError:
                                    continue

                                if file_key in self._processed_files:
                                    continue

                                # Verify that 3rd-party exporter (CapCut, Premiere, etc.) has finished writing
                                if self._is_file_ready(fpath):
                                    self._processed_files.add(file_key)
                                    net = NetworkClient()
                                    checksum = net.compute_sha256(fpath)
                                    self.on_new_video_detected(fpath, checksum)
            except Exception:
                pass
            time.sleep(2.0)

    def _is_file_ready(self, file_path: Path) -> bool:
        """
        Polls file size to ensure the external exporter (CapCut, Premiere, Blender, etc.)
        has completely finished saving the render file and closed the write lock.
        """
        try:
            if not file_path.exists() or not file_path.is_file():
                return False
            initial_size = file_path.stat().st_size
            if initial_size == 0:
                return False
            time.sleep(1.5)
            if not file_path.exists():
                return False
            final_size = file_path.stat().st_size
            if initial_size != final_size:
                return False

            # Check if file can be opened for reading exclusively (not locked by CapCut exporter)
            with open(file_path, "rb") as f:
                f.read(1024)
            return True
        except (PermissionError, OSError):
            return False

