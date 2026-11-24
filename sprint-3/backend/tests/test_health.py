def test_health_includes_required_monitoring_fields(api_client, api_state):
    api_state.redis.set("aggregator:status", "ok")
    api_state.redis.set("cache:bmkg:status", "ok")
    api_state.redis.set("cache:usgs:status", "degraded")
    response = api_client.get("/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert set(payload["komponen"]) == {
        "postgres_postgis",
        "redis_cache",
        "aggregator",
        "sumber_bmkg",
        "sumber_usgs",
    }
    assert payload["usia_cache_detik"] == {"bmkg": 0, "usgs": 0}
    assert isinstance(payload["latensi_db_ms"], int)
    assert payload["versi"] == "0.1.0"
