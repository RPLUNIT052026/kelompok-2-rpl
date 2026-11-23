from functools import lru_cache
from uuid import UUID

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+psycopg://hyperevac:hyperevac_dev_pass@localhost:5432/hyperevac"
    )
    redis_url: str = "redis://localhost:6379/0"
    bmkg_gempa_url: str = "https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json"
    bmkg_cuaca_url: str = "https://api.bmkg.go.id/publik/prakiraan-cuaca"
    bmkg_adm4: str = "11.74.02.2001"
    usgs_url: str = (
        "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
    )
    http_timeout: float = 10.0
    http_retries: int = 3
    fetch_interval_seconds: int = 60
    app_version: str = "0.1.0"
    operator_api_token: str = ""
    operator_user_id: UUID | None = None
    auth_jwt_secret: str = ""
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
