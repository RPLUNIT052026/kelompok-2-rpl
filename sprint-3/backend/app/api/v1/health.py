from datetime import datetime, timezone
from time import perf_counter

from fastapi import APIRouter, Depends, HTTPException
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.redis_client import get_redis
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


def _cache_age(redis: object, source: str) -> int:
    value = redis.get(f"cache:{source}:updated_at")
    if not value:
        return 0
    try:
        updated_at = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return 0
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)
    return max(0, int((datetime.now(timezone.utc) - updated_at).total_seconds()))


@router.get("/health", response_model=HealthResponse)
def health_check(
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
) -> HealthResponse:
    started = perf_counter()
    postgres_status = "ok"
    try:
        db.execute(text("SELECT 1"))
        db.execute(text("SELECT PostGIS_Version()"))
    except SQLAlchemyError as exc:
        postgres_status = "down"
        raise HTTPException(
            status_code=503,
            detail={"code": "DATABASE_UNAVAILABLE", "message": "PostgreSQL/PostGIS tidak tersedia"},
        ) from exc
    latency_ms = int((perf_counter() - started) * 1000)

    redis_status = "ok"
    try:
        redis.ping()
    except RedisError:
        redis_status = "down"

    def redis_value(key: str, default: str) -> str:
        try:
            return redis.get(key) or default
        except RedisError:
            return default

    components = {
        "postgres_postgis": postgres_status,
        "redis_cache": redis_status,
        "aggregator": redis_value("aggregator:status", "degraded"),
        "sumber_bmkg": redis_value("cache:bmkg:status", "degraded"),
        "sumber_usgs": redis_value("cache:usgs:status", "degraded"),
    }
    overall_status = "ok" if postgres_status == "ok" and redis_status == "ok" else "degraded"
    try:
        bmkg_age = _cache_age(redis, "bmkg")
        usgs_age = _cache_age(redis, "usgs")
    except RedisError:
        bmkg_age = usgs_age = 0
    return HealthResponse(
        status=overall_status,
        komponen=components,
        usia_cache_detik={"bmkg": bmkg_age, "usgs": usgs_age},
        latensi_db_ms=latency_ms,
        versi=get_settings().app_version,
    )
