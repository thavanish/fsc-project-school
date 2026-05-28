from functools import lru_cache
from typing import Any, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Change the type alignment to accept a Union of list or raw str on input
    allowed_origins: Union[list[str], str] = ["http://localhost:4321", "http://localhost:3000"]

    # face match threshold. the face_recognition library recommends 0.6 as a safe
    # default, but 0.55 reduces false positives without dropping real matches much.
    match_threshold: float = 0.55

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            # Check if it looks like a JSON array, try parsing it safely
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            
            # If it's a comma-separated string, split it and clean it up
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
