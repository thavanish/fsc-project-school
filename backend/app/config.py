from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    allowed_origins: str = "http://localhost:4321,http://localhost:3000,https://d593d53c.fsc-project-school.pages.dev"
    match_threshold: float = 0.55

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

        return "http://localhost:4321,http://localhost:3000,https://d593d53c.fsc-project-school.pages.dev"

    @property
    def allowed_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
