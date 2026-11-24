from app.models.enums import RoadSegmentStatus
from app.services.routing_engine import RoutingEngine
from app.models.entities import RoadSegment
from sprint3b_fakes import SEGMENT_ID, Sprint3BSession
from conftest import RW_ID


def test_operator_lists_all_road_segments_with_current_status(
    api_client, api_state, operator_headers
):
    db = Sprint3BSession()
    target = db.segments[0]
    target.status = RoadSegmentStatus.TERTUTUP_MANUAL
    target.diblokir_manual = True
    target.alasan = "Jalur tergenang"
    api_state.db = db

    response = api_client.get(
        "/v1/admin/routes/segments",
        headers=operator_headers,
        params={"rw": str(RW_ID)},
    )

    assert response.status_code == 200
    assert len(response.json()["data"]) == len(db.segments)
    blocked = next(
        item for item in response.json()["data"] if item["segment_id"] == str(SEGMENT_ID)
    )
    assert blocked["status"] == "TERTUTUP_MANUAL"
    assert blocked["diblokir_manual"] is True
    assert blocked["alasan"] == "Jalur tergenang"
    assert blocked["geometri"]["type"] == "LineString"


def test_manual_block_and_unblock_are_reflected_by_routing(api_client, api_state, operator_headers):
    db = Sprint3BSession()
    api_state.db = db

    blocked = api_client.post(
        "/v1/admin/routes/block",
        headers=operator_headers,
        json={"segment_id": str(SEGMENT_ID), "alasan": "Longsor"},
    )
    assert blocked.status_code == 200
    assert blocked.json() == {
        "segment_id": str(SEGMENT_ID),
        "status": "TERTUTUP_MANUAL",
        "diblokir_manual": True,
        "rute_dihitung_ulang": True,
    }
    blocked_routes = RoutingEngine(db).get_evacuation_routes(4.4683, 97.9683)
    assert all(
        segment["segment_id"] != str(SEGMENT_ID)
        for route in blocked_routes["rute"]
        for segment in route["segmen_dilalui"]
    )

    unblocked = api_client.delete(
        f"/v1/admin/routes/block/{SEGMENT_ID}",
        headers=operator_headers,
    )
    assert unblocked.status_code == 200
    assert unblocked.json()["status"] == "AMAN"
    assert unblocked.json()["diblokir_manual"] is False
    assert unblocked.json()["rute_dihitung_ulang"] is True
    assert db.get(RoadSegment, SEGMENT_ID).status == "AMAN"
