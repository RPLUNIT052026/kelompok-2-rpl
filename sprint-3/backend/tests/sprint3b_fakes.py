import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from geoalchemy2.shape import from_shape
from shapely.geometry import LineString, Polygon

from app.models.entities import DigitalTwin, PerangkatWarga, RoadReport, RoadSegment, RW
from app.models.enums import RoadReportStatus, RoadReportTipe, RoadSegmentStatus
from conftest import FakeSession, RW_ID

SEGMENT_ID = uuid.UUID("b7a6c5d4-0000-0000-0000-000000000032")
ALT_SEGMENT_ID = uuid.UUID("b7a6c5d4-0000-0000-0000-000000000034")
REPORT_ID = uuid.UUID("c9d8e7f6-0000-0000-0000-000000000020")
DEVICE_ID = "device-01"


def _segment(segment_id, geometry, length=100.0):
    return SimpleNamespace(
        segment_id=segment_id,
        rw_id=RW_ID,
        geometri=geometry,
        panjang_m=length,
        kecepatan_rata_rata_mps=1.4,
        kapasitas_maks=400,
        pengguna_aktif=100,
        status=RoadSegmentStatus.AMAN,
        diblokir_manual=False,
        alasan="",
    )


class Sprint3BSession(FakeSession):
    def __init__(self):
        super().__init__()
        self.devices = {
            DEVICE_ID: SimpleNamespace(
                device_id=DEVICE_ID,
                rw_id=RW_ID,
                fcm_token="test-token",
                reputasi=0.5,
                terakhir_aktif=datetime.now(timezone.utc),
            )
        }
        origin = (97.9683, 4.4683)
        destination = (97.9664134, 4.4708906)
        middle = (97.9692, 4.4675)
        alternate_middle = (97.9690, 4.4715)
        self.segments = [
            _segment(SEGMENT_ID, LineString([origin, destination]), 500.0),
            _segment(
                uuid.UUID("b7a6c5d4-0000-0000-0000-000000000033"),
                LineString([origin, middle]),
                300.0,
            ),
            _segment(
                uuid.UUID("b7a6c5d4-0000-0000-0000-000000000035"),
                LineString([middle, destination]),
                300.0,
            ),
            _segment(ALT_SEGMENT_ID, LineString([origin, alternate_middle]), 400.0),
            _segment(
                uuid.UUID("b7a6c5d4-0000-0000-0000-000000000036"),
                LineString([alternate_middle, destination]),
                400.0,
            ),
        ]
        self.reports = []
        self.twin = None
        self.distance_m = 10.0
        self.cluster_count = 2
        self.rainfall_max = 3.5
        self.correction_report_count = 1
        self.zone = from_shape(
            Polygon(
                [
                    (97.9666, 4.4693),
                    (97.9671, 4.4693),
                    (97.9671, 4.4696),
                    (97.9666, 4.4696),
                    (97.9666, 4.4693),
                ]
            ),
            srid=4326,
        )

    def get(self, model, key):
        if model is RW:
            return self.rw if self.rw_exists and key == self.rw.id else None
        if model is PerangkatWarga:
            return self.devices.get(key)
        if model is RoadSegment:
            return next((item for item in self.segments if item.segment_id == key), None)
        if model is RoadReport:
            return next((item for item in self.reports if item.id == key), None)
        return super().get(model, key)

    def scalar(self, statement):
        sql = str(statement).lower()
        if "st_distance" in sql:
            return self.distance_m
        if "count(road_report.id)" in sql and "road_report.segment_id =" in sql:
            return self.cluster_count
        if "count(road_report.id)" in sql and "road_report.segment_id in" in sql:
            return self.correction_report_count
        if "st_unaryunion" in sql:
            return self.zone
        if "count(road_segment.segment_id)" in sql:
            return sum(
                item.status
                in (
                    RoadSegmentStatus.TERTUTUP_SEMENTARA,
                    RoadSegmentStatus.TERTUTUP,
                    RoadSegmentStatus.TERTUTUP_MANUAL,
                )
                for item in self.segments
            )
        if "max(hazard.tingkat_bahaya)" in sql:
            return self.rainfall_max
        if "count(road_report.id)" in sql:
            return sum(
                item.tipe == RoadReportTipe.TERTUTUP
                and item.status == RoadReportStatus.DITERIMA
                and item.dibuat_pada >= datetime.now(timezone.utc) - timedelta(hours=1)
                for item in self.reports
            )
        if "count(perangkat_warga.device_id)" in sql:
            return len(self.devices)
        if "from digital_twin" in sql:
            return self.twin
        if "st_contains" in sql:
            return self.rw
        return self.rw

    def scalars(self, statement):
        sql = str(statement).lower()
        if "st_intersects" in sql:
            return _ReportResults([])
        if "from road_report" in sql:
            return _ReportResults(self.reports)
        if "from road_segment" in sql:
            return _ReportResults(self.segments)
        return super().scalars(statement)

    def add(self, item):
        if isinstance(item, RoadReport):
            self.reports.append(item)
        elif isinstance(item, DigitalTwin):
            if item.id is None:
                item.id = uuid.uuid4()
            self.twin = item

    def flush(self):
        return None


class _ReportResults:
    def __init__(self, values):
        self.values = values

    def all(self):
        return self.values
