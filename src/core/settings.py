"""Application settings — Pydantic Settings v2.

Centralized configuration loaded from environment variables and .env file.
"""
from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All app config in one place."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "pension-calculator"
    app_env: str = Field(default="development")
    debug: bool = False
    secret_key: str = Field(min_length=32)

    # Database
    database_url: str
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    jwt_secret: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # CORS
    cors_allowed_origins: str = "http://localhost:3000"

    @field_validator("cors_allowed_origins")
    @classmethod
    def validate_cors_not_wildcard_in_prod(cls, v: str, info) -> str:
        env = info.data.get("app_env", "development")
        if env == "production" and "*" in v:
            raise ValueError("Wildcard CORS not allowed in production")
        return v

    @property
    def cors_allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached singleton — settings loaded once per process."""
    return Settings()
