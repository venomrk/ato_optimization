from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./rko.db"

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    cors_origins: str = "http://localhost:3000"
    frontend_url: str = "http://localhost:3000"

    openrouter_api_key: str | None = None
    openrouter_model: str = "anthropic/claude-3.5-sonnet"

    serpapi_api_key: str | None = None

    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_premium_price_id: str | None = None
    stripe_success_url: str = "http://localhost:3000/profile"
    stripe_cancel_url: str = "http://localhost:3000/profile"

    redis_url: str | None = None


settings = Settings()
