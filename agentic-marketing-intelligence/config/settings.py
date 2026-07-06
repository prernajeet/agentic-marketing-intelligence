"""
config/settings.py
====================
Application-wide settings loaded from environment variables (.env).

Uses pydantic-settings so that every value is validated, type-hinted,
and can be overridden via environment variables in any deployment
(target: local dev, Docker, CI/CD, cloud).

NEVER hardcode credentials or secrets here. All secrets must come
from the environment (.env file, Docker secrets, or a secrets manager).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---------------------------------------------------------
    # Application
    # ---------------------------------------------------------
    app_name: str = Field(default="Agentic AI Marketing Intelligence Platform", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # ---------------------------------------------------------
    # FastAPI
    # ---------------------------------------------------------
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")

    # ---------------------------------------------------------
    # Streamlit
    # ---------------------------------------------------------
    streamlit_port: int = Field(default=8501, alias="STREAMLIT_PORT")

    # ---------------------------------------------------------
    # PostgreSQL Database
    # ---------------------------------------------------------
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="marketing_intelligence", alias="DB_NAME")
    db_user: str = Field(default="postgres", alias="DB_USER")
    db_password: str = Field(default="", alias="DB_PASSWORD")
    database_url: str = Field(
        default="postgresql+psycopg2://postgres:postgres@localhost:5432/marketing_intelligence",
        alias="DATABASE_URL",
    )

    # ---------------------------------------------------------
    # Google Gemini (LLM)
    # ---------------------------------------------------------
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.5-flash", alias="GEMINI_MODEL")
    gemini_temperature: float = Field(default=0.3, alias="GEMINI_TEMPERATURE")
    gemini_max_output_tokens: int = Field(default=2048, alias="GEMINI_MAX_OUTPUT_TOKENS")

    # ---------------------------------------------------------
    # Data Paths
    # ---------------------------------------------------------
    data_raw_path: str = Field(default="data/raw", alias="DATA_RAW_PATH")
    data_processed_path: str = Field(default="data/processed", alias="DATA_PROCESSED_PATH")
    data_exports_path: str = Field(default="data/exports", alias="DATA_EXPORTS_PATH")

    # ---------------------------------------------------------
    # MLOps
    # ---------------------------------------------------------
    model_registry_path: str = Field(default="mlops/model_registry", alias="MODEL_REGISTRY_PATH")
    mlflow_tracking_uri: str = Field(default="mlops/mlruns", alias="MLFLOW_TRACKING_URI")

    # ---------------------------------------------------------
    # Security
    # ---------------------------------------------------------
    secret_key: str = Field(default="insecure-dev-key", alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    # ---------------------------------------------------------
    # Derived helpers
    # ---------------------------------------------------------
    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parent.parent

    @property
    def data_raw_dir(self) -> Path:
        return self.project_root / self.data_raw_path

    @property
    def data_processed_dir(self) -> Path:
        return self.project_root / self.data_processed_path

    @property
    def data_exports_dir(self) -> Path:
        return self.project_root / self.data_exports_path

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Returns a cached singleton Settings instance.
    Using lru_cache avoids re-parsing the .env file on every import.
    """
    return Settings()


# Convenience singleton import: `from config.settings import settings`
settings = get_settings()
