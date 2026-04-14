"""Configuration management via environment variables."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from os import getenv


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings for the weekly digest."""

    environment: str
    digest_timezone: str
    log_level: str
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    email_from: str
    email_to: str
    openai_api_key: str | None
    openai_model: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Parse runtime settings from environment variables."""

    return Settings(
        environment=getenv("ENVIRONMENT", "development"),
        digest_timezone=getenv("DIGEST_TIMEZONE", "America/New_York"),
        log_level=getenv("LOG_LEVEL", "INFO"),
        smtp_host=getenv("SMTP_HOST", "smtp.example.com"),
        smtp_port=int(getenv("SMTP_PORT", "587")),
        smtp_username=getenv("SMTP_USERNAME", "weekly-digest@example.com"),
        smtp_password=getenv("SMTP_PASSWORD", "change-me"),
        email_from=getenv("EMAIL_FROM", "weekly-digest@example.com"),
        email_to=getenv("EMAIL_TO", "advisory-leadership@example.com"),
        openai_api_key=getenv("OPENAI_API_KEY"),
        openai_model=getenv("OPENAI_MODEL", "gpt-5-mini"),
    )
