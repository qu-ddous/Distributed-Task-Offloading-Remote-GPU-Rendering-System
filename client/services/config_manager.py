import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_SETTINGS: Dict[str, Any] = {
    "server_host": "127.0.0.1",
    "server_port": 8000,
    "api_token": "supersecret-render-token-change-me",
    "theme_mode": "dark",
    "default_resolution": "Original",
    "default_bitrate": "5M",
    "default_preset": "p4",
    "output_dir": str(Path.home() / "Downloads"),
    "allow_cpu_fallback": True,
    "watch_folder_enabled": True,
    "watch_folder_path": str(Path.home() / "Videos" / "RenderWatch_In")
}

class ClientConfigManager:
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is not None:
            self.config_path = config_path
        else:
            import sys
            if getattr(sys, "frozen", False):
                self.config_path = Path(sys.executable).parent / "client_settings.json"
            else:
                self.config_path = Path.cwd() / "client_settings.json"

    def load(self) -> Dict[str, Any]:
        merged = DEFAULT_SETTINGS.copy()
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    merged.update(data)
            except Exception:
                pass

        # Auto-adjust paths for current machine if pointing to a non-existent directory of another user
        try:
            out_p = Path(merged.get("output_dir", ""))
            if not out_p.exists():
                fallback_out = Path.home() / "Downloads"
                fallback_out.mkdir(parents=True, exist_ok=True)
                merged["output_dir"] = str(fallback_out)
        except Exception:
            merged["output_dir"] = str(Path.home() / "Downloads")

        try:
            watch_p = Path(merged.get("watch_folder_path", ""))
            if not watch_p.exists():
                fallback_watch = Path.home() / "Videos" / "RenderWatch_In"
                fallback_watch.mkdir(parents=True, exist_ok=True)
                merged["watch_folder_path"] = str(fallback_watch)
        except Exception:
            merged["watch_folder_path"] = str(Path.home() / "Videos" / "RenderWatch_In")

        return merged

    def save(self, settings: Dict[str, Any]):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Failed to save settings: {e}")

config_manager = ClientConfigManager()
