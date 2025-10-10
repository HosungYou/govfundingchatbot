"""Centralized configuration using environment variables."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env files."""

    environment: str = Field(default="development")

    # Data sources
    nsf_awards_api: AnyHttpUrl = Field(
        default="https://api.nsf.gov/services/v1/awards.json",
        description="NSF awards API base endpoint",
    )
    nsf_awards_window_days: int = Field(default=1, ge=1, le=30)

    grants_xml_url: AnyHttpUrl = Field(
        default="https://www.grants.gov/grantsws/rest/opportunity/details",
        description="Endpoint serving Grants.gov opportunity XML snapshot",
    )

    # Storage
    s3_bucket: Optional[str] = Field(default=None, description="S3 bucket for raw/staging data")
    local_data_dir: Path = Field(default=Path("data"))

    # Database
    database_url: Optional[str] = Field(default=None, description="Postgres connection string")

    # Vector store
    pinecone_api_key: Optional[str] = None
    pinecone_index: str = Field(default="govfunding-opportunities")
    pinecone_region: str = Field(default="us-east-1")

    chroma_persist_dir: Path = Field(default=Path("chroma_storage"))

    # Logging/telemetry
    log_level: str = Field(default="INFO")
    slack_webhook_url: Optional[AnyHttpUrl] = None

    model_config = SettingsConfigDict(env_file=".env", env_prefix="GOVFUNDING_", case_sensitive=False)


def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()
