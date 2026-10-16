"""Application settings - Pydantic Settings v2.

Centralized configuration loaded from environment variables and .env file.
"""
from functools import lru_cache
from typing import List

from pydantic import Field, field_validator, model_validator
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
    secret_key: str = Field(
        default="dev-secret-key-change-in-production-min-32-chars",
        min_length=32,
    )
    log_level: str = "INFO"

    # CORS - string con origins separados por coma
    # Ej: "https://example.com,https://www.example.com"
    cors_allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000"
    )

    # Database (opcional para MVP)
    database_url: str = "postgresql+asyncpg://user:pass@localhost/db"
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # Redis (opcional para MVP)
    redis_url: str = "redis://localhost:6379/0"

    @field_validator("app_env")
    @classmethod
    def validate_app_env(cls, v: str) -> str:
        """Valida que app_env sea un valor permitido."""
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"app_env must be one of {allowed}")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Valida que log_level sea un nivel estandar."""
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v_upper

    @model_validator(mode="after")
    def validate_cors_in_production(self):
        """Rechaza CORS wildcard en produccion por seguridad."""
        if self.app_env == "production":
            for origin in self.cors_allowed_origins_list:
                if origin == "*":
                    raise ValueError(
                        "Wildcard CORS not allowed in production. "
                        "Set explicit origins in CORS_ALLOWED_ORIGINS."
                    )
        return self

    @property
    def cors_allowed_origins_list(self) -> List[str]:
        if not self.cors_allowed_origins:
            return []
        return [
            origin.strip()
            for origin in self.cors_allowed_origins.split(",")
            if origin.strip()
        ]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    """Cached singleton - settings loaded once per process."""
    return Settings()
