from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_ALLOWED_ORIGINS = (
    "http://localhost:4321,"
    "http://localhost:3000,"
    "https://d593d53c.fsc-project-school.pages.dev,"
    "https://face.thavanish.dedyn.io,"
    "https://fsc-project-school.vercel.app"
)


class Settings(BaseSettings):
    allowed_origins: str = DEFAULT_ALLOWED_ORIGINS
    match_threshold: float = 0.55
    ambiguity_margin: float = 0.035
    max_upload_bytes: int = 4_300_000
    image_max_side: int = 960
    detection_upsample: int = 1
    register_jitters: int = 2
    query_jitters: int = 1
    face_model: str = "small"
    storage_backend: str = "auto"
    storage_file: str = "data/faces.json"
    blob_path: str = "face-db/faces.json"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, v: Any) -> str:
        if isinstance(v, list):
            return ",".join(str(item).strip() for item in v if str(item).strip())

        if isinstance(v, str):
            value = v.strip()

            if value.startswith("[") and value.endswith("]"):
                import json

                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return ",".join(str(item).strip() for item in parsed if str(item).strip())
                except json.JSONDecodeError:
                    pass

            return value

        return DEFAULT_ALLOWED_ORIGINS

    @property
    def allowed_origin_list(self) -> list[str]:
        configured = [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
        defaults = [origin.strip() for origin in DEFAULT_ALLOWED_ORIGINS.split(",") if origin.strip()]
        return sorted(set(configured + defaults))

    @property
    def use_blob_storage(self) -> bool:
        import os

        backend = self.storage_backend.strip().lower()
        if backend == "blob":
            return True
        if backend == "local":
            return False
        return bool(os.getenv("VERCEL") and os.getenv("BLOB_READ_WRITE_TOKEN"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
