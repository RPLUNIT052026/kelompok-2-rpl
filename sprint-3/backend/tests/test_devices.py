from conftest import RW_ID


def test_register_device_and_upsert_preserves_reputation(api_client, api_state):
    payload = {
        "device_id": "device-01",
        "fcm_token": "token-first",
        "rw_id": str(RW_ID),
    }

    created = api_client.post("/v1/devices/register", json=payload)
    assert created.status_code == 201
    assert created.json()["reputasi"] == 0.5
    assert created.json()["terdaftar"] is True

    payload["fcm_token"] = "token-updated"
    updated = api_client.post("/v1/devices/register", json=payload)
    assert updated.status_code == 201
    assert api_state.db.devices["device-01"].fcm_token == "token-updated"
    assert api_state.db.devices["device-01"].reputasi == 0.5


def test_register_device_rejects_unknown_rw(api_client, api_state):
    api_state.db.rw_exists = False
    response = api_client.post(
        "/v1/devices/register",
        json={"device_id": "device-02", "fcm_token": "token", "rw_id": str(RW_ID)},
    )
    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "NOT_FOUND",
            "message": "RW tidak ditemukan",
            "details": [],
        }
    }
