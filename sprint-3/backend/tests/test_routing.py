import uuid
from types import SimpleNamespace

from geoalchemy2.shape import from_shape
from shapely.geometry import LineString, Point

from app.models.enums import RoadSegmentStatus
from app.services.routing_engine import EMERGENCY_MESSAGE, RoutingEngine
from conftest import RW_ID, sample_rw


def _segment(segment_id: int, start, end, length, active, capacity=100, status=RoadSegmentStatus.AMAN):
    return SimpleNamespace(
        segment_id=uuid.UUID(f"b7a6c5d4-0000-0000-0000-{segment_id:012d}"),
        rw_id=RW_ID,
        geometri=LineString([start, end]),
        panjang_m=length,
        kecepatan_rata_rata_mps=1.4,
        kapasitas_maks=capacity,
        pengguna_aktif=active,
        status=status,
        diblokir_manual=False,
        alasan="",
    )


class RoutingSession:
    def __init__(self, segments, impacted_ids=()):
        self.rw = sample_rw()
        self.segments = segments
        self.impacted_ids = impacted_ids
        self.statements = []
        self.commits = 0

    def scalar(self, statement):
        return self.rw

    def scalars(self, statement):
        self.statements.append(str(statement))
        if "ST_Intersects" in str(statement):
            return SimpleNamespace(all=lambda: list(self.impacted_ids))
        return SimpleNamespace(all=lambda: self.segments)

    def commit(self):
        self.commits += 1


def test_routing_avoids_st_intersects_hazards():
    origin = (97.9683, 4.4683)
    destination = (97.9664134, 4.4708906)
    hazard_middle = (97.9672, 4.4688)
    safe_middle = (97.9692, 4.4675)
    hazard_a = _segment(30, origin, hazard_middle, 100, 10)
    hazard_b = _segment(31, hazard_middle, destination, 100, 10)
    safe_a = _segment(32, origin, safe_middle, 150, 10)
    safe_b = _segment(33, safe_middle, destination, 150, 10)
    db = RoutingSession([hazard_a, hazard_b, safe_a, safe_b], [hazard_a.segment_id, hazard_b.segment_id])

    result = RoutingEngine(db).get_evacuation_routes(4.4683, 97.9683)

    assert "ST_Intersects" in db.statements[0]
    assert all(
        segment["segment_id"] not in {str(hazard_a.segment_id), str(hazard_b.segment_id)}
        for segment in result["rute"][0]["segmen_dilalui"]
    )
    assert result["evakuasi_vertikal"] is False


def test_anti_bottleneck_selects_lowest_load_alternative():
    origin = (97.9683, 4.4683)
    destination = (97.9664134, 4.4708906)
    saturated_middle = (97.9672, 4.469)
    alternate_middle = (97.9692, 4.4675)
    saturated_a = _segment(40, origin, saturated_middle, 100, 90)
    saturated_b = _segment(41, saturated_middle, destination, 100, 85)
    alternate_a = _segment(42, origin, alternate_middle, 300, 10)
    alternate_b = _segment(43, alternate_middle, destination, 300, 10)
    db = RoutingSession([saturated_a, saturated_b, alternate_a, alternate_b])
    db.rw.titik_kumpul = from_shape(Point(*destination), srid=4326)

    result = RoutingEngine(db).get_evacuation_routes(4.4683, 97.9683)

    assert len(result["rute"]) == 2
    assert result["rute"][0]["utama"] is False
    assert result["rute"][1]["utama"] is True
    assert alternate_a.pengguna_aktif == 11


def test_all_unsafe_segments_returns_vertical_evacuation():
    closed = _segment(
        50,
        (97.9683, 4.4683),
        (97.9664134, 4.4708906),
        100,
        10,
        status=RoadSegmentStatus.TERTUTUP,
    )
    result = RoutingEngine(RoutingSession([closed])).get_evacuation_routes(4.4683, 97.9683)

    assert result["evakuasi_vertikal"] is True
    assert result["alert_sar"] is True
    assert result["pesan_darurat"] == EMERGENCY_MESSAGE
    assert result["rute"] == []
