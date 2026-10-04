import os
import json
from pathlib import Path
from typing import Dict, Any

DEFAULT_SETTINGS: Dict[str, Any] = {
    "server_host": "127.0.0.1",
    "server_port": 8000,
    "api_token": "supersecret-render-token-change-me",
    "theme_mode": "dark",
    "default_resolution": "Original",
    "default_bitrate": "5M",
    "default_preset": "p4",
    "output_dir": str(Path.home() / "Downloads"),
    "allow_cpu_fallback": False
}

class ClientConfigManager:
    def __init__(self, config_path: Path = Path("client_settings.json")):
        self.config_path = config_path

    def load(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            return DEFAULT_SETTINGS.copy()
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                merged = DEFAULT_SETTINGS.copy()
                merged.update(data)
                return merged
        except Exception:
            return DEFAULT_SETTINGS.copy()

    def save(self, settings: Dict[str, Any]):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Failed to save settings: {e}")

config_manager = ClientConfigManager()
