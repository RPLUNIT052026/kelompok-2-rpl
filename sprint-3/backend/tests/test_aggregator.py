import asyncio
from datetime import datetime, timezone

import httpx

from app.core.config import Settings
from app.services.aggregator import DataAggregator
from conftest import FakeRedis, FakeSession, RW_ID


def _settings():
    return Settings(
        database_url="postgresql+psycopg://user:pass@localhost/db",
        bmkg_gempa_url="https://mock.local/quake",
        bmkg_cuaca_url="https://mock.local/weather",
        bmkg_adm4="11.74.02.2001",
        usgs_url="https://mock.local/usgs",
        http_retries=3,
    )


def test_successful_aggregator_cycle_persists_hazards_and_cache():
    def handler(request):
        if request.url.path == "/quake":
            return httpx.Response(
                200,
                json={
                    "Infogempa": {
                        "gempa": {
                            "Coordinates": "4.4683,97.9683",
                            "Magnitude": "6.7",
                            "DateTime": "2026-09-29T08:00:00Z",
                            "Tanggal": "29 Sep 2026",
                            "Potensi": "Tidak berpotensi tsunami",
                        }
                    }
                },
            )
        if request.url.path == "/weather":
            return httpx.Response(200, json={"data": []})
        return httpx.Response(
            200,
            json={
                "features": [
                    {
                        "id": "usgs-event-1",
                        "geometry": {"type": "Point", "coordinates": [97.9683, 4.4683, 10]},
                        "properties": {"mag": 5.5, "time": 1790668800000, "tsunami": 0},
                    }
                ]
            },
        )

    async def no_wait(_):
        return None

    async def run():
        db = FakeSession()
        redis = FakeRedis()
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            statuses = await DataAggregator(
                db, redis, _settings(), http_client=client, sleep=no_wait
            ).run_cycle()
        return db, redis, statuses

    db, redis, statuses = asyncio.run(run())
    assert statuses == {"bmkg": "ok", "usgs": "ok"}
    assert len(db.merged) == 2
    assert all(hazard.rw_id == RW_ID for hazard in db.merged)
    assert redis.get("cache:bmkg:status") == "ok"
    assert redis.get("cache:usgs:status") == "ok"
    assert redis.get("cache:meta:data_kedaluwarsa") == "false"
    assert redis.get("aggregator:status") == "ok"


def test_timeout_retries_then_uses_cache_and_marks_expired():
    requests = []
    delays = []

    def handler(request):
        requests.append(request)
        raise httpx.ReadTimeout("mock timeout")

    async def no_wait(delay):
        delays.append(delay)

    async def run():
        db = FakeSession()
        redis = FakeRedis()
        redis.set("cache:bmkg:payload", '{"earthquake": {}}')
        redis.set("cache:usgs:payload", '{"features": []}')
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            statuses = await DataAggregator(
                db, redis, _settings(), http_client=client, sleep=no_wait
            ).run_cycle()
        return db, redis, statuses

    db, redis, statuses = asyncio.run(run())
    assert len(requests) == 9
    assert delays == [1, 2, 4] * 3
    assert statuses == {"bmkg": "degraded", "usgs": "degraded"}
    assert redis.get("cache:meta:data_kedaluwarsa") == "true"
    assert redis.get("aggregator:status") == "degraded"
    assert db.rw.data_kedaluwarsa is True


def test_invalid_coordinates_are_rejected_and_logged(caplog):
    async def run():
        return DataAggregator(FakeSession(), FakeRedis(), _settings()).normalizePayload(
            "usgs",
            {
                "features": [
                    {
                        "id": "bad-event",
                        "geometry": {"type": "Point", "coordinates": [97.9683, 999, 10]},
                        "properties": {"mag": 4.5, "time": datetime.now(timezone.utc).timestamp()},
                    }
                ]
            },
        )

    normalized = asyncio.run(run())
    assert normalized == []
    assert "Discarded invalid USGS" in caplog.text


def test_bmkg_parser_normalizes_date_and_prototype_rainfall_thresholds():
    aggregator = DataAggregator(FakeSession(), FakeRedis(), _settings())
    normalized = aggregator.normalizePayload(
        "bmkg",
        {
            "earthquake": {
                "Infogempa": {
                    "gempa": {
                        "Coordinates": "6 LS, 106 BT",
                        "Magnitude": "5.0",
                        "Tanggal": "29 Sep 2026",
                        "Jam": "08:00:00 WIB",
                        "Potensi": "Tidak berpotensi tsunami",
                    }
                }
            },
            "weather": {
                "lokasi": {"adm4": "11.74.02.2001", "lat": "4.4683", "lon": "97.9683"},
                "data": [{"cuaca": [[{"tp": "20", "weather_desc": "Hujan sedang"}]]}],
            },
        },
    )

    assert len(normalized) == 2
    assert normalized[0]["level_bahaya"].value == "WASPADA"
    assert normalized[0]["waktu_data"].isoformat() == "2026-09-29T08:00:00+00:00"
    assert normalized[1]["level_bahaya"].value == "SIAGA"
