from pydantic import BaseModel


class HealthComponents(BaseModel):
    postgres_postgis: str
    redis_cache: str
    aggregator: str
    sumber_bmkg: str
    sumber_usgs: str


class CacheAge(BaseModel):
    bmkg: int
    usgs: int


class HealthResponse(BaseModel):
    status: str
    komponen: HealthComponents
    usia_cache_detik: CacheAge
    latensi_db_ms: int
    versi: str
