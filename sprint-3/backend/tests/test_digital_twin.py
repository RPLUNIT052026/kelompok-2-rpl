from conftest import RW_ID
from sprint3b_fakes import SEGMENT_ID, Sprint3BSession


def test_twin_returns_refreshed_software_estimates(api_client, api_state, operator_headers):
    db = Sprint3BSession()
    db.rainfall_max = 3.5
    db.correction_report_count = 2
    api_state.db = db

    response = api_client.get(f"/v1/twin/{RW_ID}", headers=operator_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["rw_id"] == str(RW_ID)
    assert payload["zona_bahaya"]["type"] == "Polygon"
    assert payload["tinggi_genangan_cm"] == 45.0
    assert payload["ruas_tertutup"] == 0
    assert payload["perangkat_aktif"] == 1
    assert payload["estimasi_warga_terdampak"] == 1
    assert payload["diperbarui_pada"].endswith("Z")
    assert db.twin is not None


def test_twin_refreshes_closed_road_count_after_manual_block(
    api_client, api_state, operator_headers
):
    db = Sprint3BSession()
    api_state.db = db
    block_response = api_client.post(
        "/v1/admin/routes/block",
        headers=operator_headers,
        json={"segment_id": str(SEGMENT_ID), "alasan": "Banjir"},
    )
    assert block_response.status_code == 200

    twin_response = api_client.get(f"/v1/twin/{RW_ID}", headers=operator_headers)

    assert twin_response.status_code == 200
    assert twin_response.json()["ruas_tertutup"] == 1
