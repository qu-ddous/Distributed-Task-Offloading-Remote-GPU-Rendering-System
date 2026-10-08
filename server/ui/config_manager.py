import json
from pathlib import Path
from typing import Dict, Any

SERVER_SETTINGS_FILE = Path("server_settings.json")

DEFAULT_SERVER_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "api_token": "supersecret-render-token-change-me",
    "start_minimized": False,
    "auto_clean_temp": True,
    "max_concurrent_jobs": 1,
    "allow_cpu_fallback": True,
    "output_folder": "storage/output",
    "temp_folder": "storage/jobs",
    "default_resolution": "1920 x 1080 (1080p)",
    "default_bitrate": "5 Mbps",
    "default_preset": "P4 - Balanced",
    "default_container": "MP4 (H.264)",
    "log_retention_days": 30
}

class ServerConfigManager:
    @staticmethod
    def load() -> Dict[str, Any]:
        if SERVER_SETTINGS_FILE.exists():
            try:
                with open(SERVER_SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cfg = dict(DEFAULT_SERVER_CONFIG)
                    cfg.update(data)
                    return cfg
            except Exception:
                pass
        return dict(DEFAULT_SERVER_CONFIG)

    @staticmethod
    def save(config: Dict[str, Any]):
        try:
            with open(SERVER_SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"[ServerConfigManager] Error saving config: {e}")

server_config_manager = ServerConfigManager()

