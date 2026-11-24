from conftest import HAZARD_ID, RW_ID


def test_hazards_response_has_rw_and_source_attribution(api_client, api_state):
    response = api_client.get(f"/v1/hazards?rw={RW_ID}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["rw"]["nama_rw"] == "RW 05 — Gampong Jawa, Langsa Kota"
    assert payload["rw"]["batas_wilayah"]["type"] == "Polygon"
    assert payload["rw"]["titik_kumpul"]["type"] == "Point"
    assert payload["hazards"][0]["id"] == str(HAZARD_ID)
    assert payload["hazards"][0]["sumber"] == "BMKG"
    assert payload["hazards"][0]["level_bahaya"] == "SIAGA"
    assert payload["data_kedaluwarsa"] is False


def test_hazards_response_marks_cached_data_expired(api_client, api_state):
    api_state.redis.set("cache:meta:data_kedaluwarsa", "true")
    response = api_client.get(f"/v1/hazards?rw={RW_ID}")

    assert response.status_code == 200
    assert response.json()["data_kedaluwarsa"] is True


def test_hazards_returns_standard_404_for_unknown_rw(api_client, api_state):
    api_state.db.rw_exists = False
    response = api_client.get(f"/v1/hazards?rw={RW_ID}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
