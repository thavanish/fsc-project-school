from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # origins allowed to talk to this API — update ALLOWED_ORIGINS in .env
    allowed_origins: list[str] = ["http://localhost:4321", "http://localhost:3000"]

    # face match threshold. the face_recognition library recommends 0.6 as a safe
    # default, but 0.55 reduces false positives without dropping real matches much.
    match_threshold: float = 0.55

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
