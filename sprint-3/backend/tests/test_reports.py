from datetime import datetime, timezone

from sprint3b_fakes import DEVICE_ID, SEGMENT_ID, Sprint3BSession


def _report_body(report_type="tertutup"):
    return {
        "device_id": DEVICE_ID,
        "segment_id": str(SEGMENT_ID),
        "tipe": report_type,
        "lat": 4.4683,
        "lng": 97.9683,
        "catatan": "Jalan tergenang",
        "dibuat_pada": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def test_trusted_closed_report_marks_segment_temporary_closed(api_client, api_state):
    db = Sprint3BSession()
    db.devices[DEVICE_ID].reputasi = 0.9
    api_state.db = db

    response = api_client.post("/v1/reports", json=_report_body())

    assert response.status_code == 201
    payload = response.json()
    assert payload["skor_kepercayaan"] >= 0.75
    assert payload["status"] == "terverifikasi_otomatis"
    assert payload["road_segment_status"] == "TERTUTUP_SEMENTARA"
    assert payload["rute_dihitung_ulang"] is True


def test_high_trust_safe_report_never_opens_or_auto_closes_segment(api_client, api_state):
    db = Sprint3BSession()
    db.devices[DEVICE_ID].reputasi = 0.9
    api_state.db = db

    response = api_client.post("/v1/reports", json=_report_body("aman"))

    assert response.status_code == 201
    payload = response.json()
    assert payload["skor_kepercayaan"] >= 0.75
    assert payload["status"] == "menunggu_tinjauan"
    assert payload["road_segment_status"] == "MENUNGGU_TINJAUAN"
    assert payload["rute_dihitung_ulang"] is False


def test_low_trust_closed_report_waits_for_operator(api_client, api_state):
    db = Sprint3BSession()
    db.distance_m = 100.0
    db.cluster_count = 0
    api_state.db = db

    response = api_client.post("/v1/reports", json=_report_body())

    assert response.status_code == 201
    assert response.json()["status"] == "menunggu_tinjauan"
    assert response.json()["road_segment_status"] == "MENUNGGU_TINJAUAN"
    assert response.json()["rute_dihitung_ulang"] is False


def test_score_below_threshold_is_not_rounded_into_auto_verification(api_client, api_state):
    db = Sprint3BSession()
    db.devices[DEVICE_ID].reputasi = 0.615
    db.cluster_count = 1
    api_state.db = db

    response = api_client.post("/v1/reports", json=_report_body())

    assert response.status_code == 201
    assert response.json()["skor_kepercayaan"] < 0.75
    assert response.json()["status"] == "menunggu_tinjauan"
    assert response.json()["rute_dihitung_ulang"] is False
