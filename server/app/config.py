import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_TOKEN: str = "supersecret-render-token-change-me"
    STORAGE_DIR: str = "storage/jobs"
    MAX_UPLOAD_SIZE: int = 2 * 1024 * 1024 * 1024  # 2 GB
    MAX_CONCURRENT_JOBS: int = 1
    ALLOW_CPU_FALLBACK: bool = False
    JOB_RETENTION_HOURS: int = 24

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def storage_path(self) -> Path:
        p = Path(self.STORAGE_DIR)
        if not p.is_absolute():
            # Relative to server app base or working dir
            p = Path.cwd() / p
        p.mkdir(parents=True, exist_ok=True)
        return p

settings = Settings()
