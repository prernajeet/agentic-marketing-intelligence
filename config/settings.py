from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = Field(default="postgresql://marketing_user:marketing_pass@localhost:5432/marketing_db")

    # Gemini
    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="gemini-2.5-flash")

    # API
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_debug: bool = Field(default=False)
    secret_key: str = Field(default="change_me")

    # MLOps
    mlops_model_dir: str = Field(default="mlops/model_registry")
    mlops_experiment_tracking: bool = Field(default=True)

    # Data dirs
    data_raw_dir: str = Field(default="data/raw")
    data_processed_dir: str = Field(default="data/processed")
    data_exports_dir: str = Field(default="data/exports")

    # Derived
    @property
    def model_registry_path(self) -> Path:
        return BASE_DIR / self.mlops_model_dir

    @property
    def raw_data_path(self) -> Path:
        return BASE_DIR / self.data_raw_dir

    @property
    def processed_data_path(self) -> Path:
        return BASE_DIR / self.data_processed_dir

    @property
    def exports_data_path(self) -> Path:
        return BASE_DIR / self.data_exports_dir

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
