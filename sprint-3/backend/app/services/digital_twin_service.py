import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from geoalchemy2.shape import to_shape
from shapely.geometry import mapping
from shapely.geometry.base import BaseGeometry
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.entities import DigitalTwin, Hazard, PerangkatWarga, RoadReport, RoadSegment, RW
from app.models.enums import LevelBahaya, RoadReportStatus, RoadReportTipe, RoadSegmentStatus
from app.schemas.twin import DigitalTwinResponse

_ACTIVE_HAZARDS = (LevelBahaya.WASPADA, LevelBahaya.SIAGA, LevelBahaya.AWAS)
_CLOSED_SEGMENTS = (
    RoadSegmentStatus.TERTUTUP_SEMENTARA,
    RoadSegmentStatus.TERTUTUP,
    RoadSegmentStatus.TERTUTUP_MANUAL,
)


def _geojson(geometry: Any) -> dict[str, Any] | None:
    if geometry is None:
        return None
    shaped = geometry if isinstance(geometry, BaseGeometry) else to_shape(geometry)
    return mapping(shaped)


class DigitalTwinService:
    """Build software estimates from hazards, verified reports, and app registrations."""

    def __init__(self, db: Session):
        self.db = db

    def refresh_snapshot(
        self,
        rw_id: uuid.UUID,
        manual_override_cm: float | None = None,
        *,
        commit: bool = True,
    ) -> DigitalTwinResponse:
        rw = self.db.get(RW, rw_id)
        if rw is None:
            raise LookupError("RW tidak ditemukan")
        if manual_override_cm is not None and manual_override_cm < 0:
            raise ValueError("Override tinggi genangan tidak boleh negatif")

        zone = self.db.scalar(
            select(func.ST_UnaryUnion(func.ST_Collect(Hazard.geometri))).where(
                Hazard.rw_id == rw_id,
                Hazard.level_bahaya.in_(_ACTIVE_HAZARDS),
            )
        )
        closed_segments = self.db.scalar(
            select(func.count(RoadSegment.segment_id)).where(
                RoadSegment.rw_id == rw_id,
                RoadSegment.status.in_(_CLOSED_SEGMENTS),
            )
        )
        rainfall_cm = self.db.scalar(
            select(func.max(Hazard.tingkat_bahaya)).where(
                Hazard.rw_id == rw_id,
                Hazard.sumber == "BMKG",
                Hazard.jenis.in_(("cuaca_ekstrem", "curah_hujan")),
                Hazard.level_bahaya.in_(_ACTIVE_HAZARDS),
            )
        )
        correction_reports = self.db.scalar(
            select(func.count(RoadReport.id)).where(
                RoadReport.segment_id.in_(
                    select(RoadSegment.segment_id).where(RoadSegment.rw_id == rw_id)
                ),
                RoadReport.tipe == RoadReportTipe.TERTUTUP,
                RoadReport.status == RoadReportStatus.DITERIMA,
                RoadReport.dibuat_pada >= datetime.now(timezone.utc) - timedelta(hours=1),
            )
        )
        active_devices = self.db.scalar(
            select(func.count(PerangkatWarga.device_id)).where(
                PerangkatWarga.rw_id == rw_id,
                PerangkatWarga.terakhir_aktif
                >= datetime.now(timezone.utc) - timedelta(hours=24),
            )
        )

        estimated_water_cm = max(float(rainfall_cm or 0.0), 0.0) * 10.0
        estimated_water_cm += max(int(correction_reports or 0), 0) * 5.0
        if manual_override_cm is not None:
            estimated_water_cm = manual_override_cm
        device_count = max(int(active_devices or 0), 0)

        snapshot = self.db.scalar(select(DigitalTwin).where(DigitalTwin.rw_id == rw_id))
        if snapshot is None:
            snapshot = DigitalTwin(rw_id=rw_id)
            self.db.add(snapshot)
        snapshot.zona_bahaya = zone
        snapshot.tinggi_genangan_cm = estimated_water_cm
        snapshot.ruas_tertutup = max(int(closed_segments or 0), 0)
        snapshot.perangkat_aktif = device_count
        snapshot.estimasi_warga_terdampak = device_count
        snapshot.diperbarui_pada = datetime.now(timezone.utc)
        self.db.flush()
        if commit:
            self.db.commit()
        return DigitalTwinResponse(
            id=snapshot.id,
            rw_id=snapshot.rw_id,
            zona_bahaya=_geojson(snapshot.zona_bahaya),
            tinggi_genangan_cm=snapshot.tinggi_genangan_cm,
            ruas_tertutup=snapshot.ruas_tertutup,
            estimasi_warga_terdampak=snapshot.estimasi_warga_terdampak,
            perangkat_aktif=snapshot.perangkat_aktif,
            diperbarui_pada=snapshot.diperbarui_pada,
        )
