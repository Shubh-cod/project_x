"""Application settings via pydantic-settings (env vars)."""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "NovaCRM"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/novacrm"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_password: str = ""

    # JWT
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # ARQ
    arq_redis_url: str = "redis://localhost:6379/1"

    # Rate limiting
    rate_limit_requests_per_minute: int = 60

    # CORS
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def refresh_token_expire_seconds(self) -> int:
        return self.refresh_token_expire_days * 24 * 60 * 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
