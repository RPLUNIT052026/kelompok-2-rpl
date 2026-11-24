from datetime import timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

from geoalchemy2 import Geography
from sqlalchemy import cast, func, select
from sqlalchemy.orm import Session

from app.models.entities import PerangkatWarga, RoadReport, RoadSegment
from app.models.enums import RoadReportStatus, RoadReportTipe, RoadSegmentStatus
from app.schemas.admin_route import ManualBlockResponse
from app.schemas.report import (
    AdminReportVerificationResponse,
    ReportCreateRequest,
    ReportCreateResponse,
)
from app.services.digital_twin_service import DigitalTwinService
from app.services.routing_engine import RoutingEngine

_AUTO_VERIFY_THRESHOLD = 0.75


def _enum_value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _refresh_routing_and_twin(db: Session, rw_id: UUID) -> None:
    RoutingEngine.invalidate_routes(db, rw_id)
    DigitalTwinService(db).refresh_snapshot(rw_id, commit=False)


class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def submit_report(self, payload: ReportCreateRequest) -> ReportCreateResponse:
        device = self.db.get(PerangkatWarga, payload.device_id)
        if device is None:
            raise LookupError("Perangkat warga tidak ditemukan")
        segment = self.db.get(RoadSegment, payload.segment_id)
        if segment is None:
            raise LookupError("Ruas jalan tidak ditemukan")

        report_time = payload.dibuat_pada.astimezone(timezone.utc)
        origin = func.ST_SetSRID(func.ST_MakePoint(payload.lng, payload.lat), 4326)
        distance = self.db.scalar(
            select(
                func.ST_Distance(
                    cast(RoadSegment.geometri, Geography(srid=4326)),
                    cast(origin, Geography(srid=4326)),
                )
            ).where(RoadSegment.segment_id == payload.segment_id)
        )
        proximity_weight = 1.0 if distance is not None and float(distance) <= 50.0 else 0.2
        cluster_count = self.db.scalar(
            select(func.count(RoadReport.id)).where(
                RoadReport.segment_id == payload.segment_id,
                RoadReport.tipe == payload.tipe,
                RoadReport.dibuat_pada >= report_time - timedelta(minutes=15),
                RoadReport.dibuat_pada <= report_time,
            )
        )
        cluster_size = max(int(cluster_count or 0), 0) + 1
        score = (
            (0.4 * float(device.reputasi))
            + (0.3 * proximity_weight)
            + (0.3 * min(cluster_size / 3, 1.0))
        )

        reroute = False
        if payload.tipe == RoadReportTipe.TERTUTUP and score >= _AUTO_VERIFY_THRESHOLD:
            report_status = RoadReportStatus.TERVERIFIKASI_OTOMATIS
            if (
                not segment.diblokir_manual
                and _enum_value(segment.status) != RoadSegmentStatus.TERTUTUP.value
            ):
                segment.status = RoadSegmentStatus.TERTUTUP_SEMENTARA
            reroute = True
        else:
            report_status = RoadReportStatus.MENUNGGU_TINJAUAN
            if _enum_value(segment.status) == RoadSegmentStatus.AMAN.value:
                segment.status = RoadSegmentStatus.MENUNGGU_TINJAUAN

        report = RoadReport(
            id=uuid4(),
            segment_id=payload.segment_id,
            device_id=payload.device_id,
            tipe=payload.tipe,
            lat=payload.lat,
            lng=payload.lng,
            catatan=payload.catatan,
            skor_kepercayaan=score,
            status=report_status,
            dibuat_pada=report_time,
        )
        self.db.add(report)
        self.db.flush()
        if reroute:
            _refresh_routing_and_twin(self.db, segment.rw_id)
        self.db.commit()
        return ReportCreateResponse(
            id=report.id,
            segment_id=report.segment_id,
            skor_kepercayaan=report.skor_kepercayaan,
            status=report.status,
            road_segment_status=segment.status,
            rute_dihitung_ulang=reroute,
        )

    def verify_report(
        self, report_id: UUID, decision: str, operator_id: UUID
    ) -> AdminReportVerificationResponse:
        report = self.db.get(RoadReport, report_id)
        if report is None:
            raise LookupError("Laporan tidak ditemukan")
        if _enum_value(report.status) in {
            RoadReportStatus.DITERIMA.value,
            RoadReportStatus.DITOLAK.value,
        }:
            raise ValueError("Laporan sudah diputuskan")

        segment = self.db.get(RoadSegment, report.segment_id)
        device = self.db.get(PerangkatWarga, report.device_id)
        if segment is None or device is None:
            raise LookupError("Ruas jalan atau perangkat warga tidak ditemukan")

        report.status = RoadReportStatus(decision)
        report.diverifikasi_oleh = operator_id
        if report.status == RoadReportStatus.DITERIMA:
            device.reputasi = min(1.0, float(device.reputasi) + 0.10)
        else:
            device.reputasi = max(0.0, float(device.reputasi) - 0.15)

        reroute = False
        if not segment.diblokir_manual:
            segment_status = _enum_value(segment.status)
            report_type = _enum_value(report.tipe)
            if report.status == RoadReportStatus.DITERIMA:
                segment.status = (
                    RoadSegmentStatus.TERTUTUP
                    if report_type == RoadReportTipe.TERTUTUP.value
                    else RoadSegmentStatus.AMAN
                )
                reroute = True
            elif segment_status == RoadSegmentStatus.TERTUTUP_SEMENTARA.value:
                segment.status = RoadSegmentStatus.AMAN
                reroute = True
            elif segment_status == RoadSegmentStatus.MENUNGGU_TINJAUAN.value:
                segment.status = RoadSegmentStatus.AMAN

        self.db.flush()
        if reroute:
            _refresh_routing_and_twin(self.db, segment.rw_id)
        self.db.commit()
        return AdminReportVerificationResponse(
            id=report.id,
            status=report.status,
            road_segment_status=segment.status,
            reputasi_diperbarui=True,
            rute_dihitung_ulang=reroute,
        )

    def block_segment(self, segment_id: UUID, reason: str) -> ManualBlockResponse:
        segment = self.db.get(RoadSegment, segment_id)
        if segment is None:
            raise LookupError("Ruas jalan tidak ditemukan")
        segment.status = RoadSegmentStatus.TERTUTUP_MANUAL
        segment.diblokir_manual = True
        segment.alasan = reason
        self.db.flush()
        _refresh_routing_and_twin(self.db, segment.rw_id)
        self.db.commit()
        return ManualBlockResponse(
            segment_id=segment.segment_id,
            status=segment.status,
            diblokir_manual=segment.diblokir_manual,
            rute_dihitung_ulang=True,
        )

    def unblock_segment(self, segment_id: UUID) -> ManualBlockResponse:
        segment = self.db.get(RoadSegment, segment_id)
        if segment is None:
            raise LookupError("Ruas jalan tidak ditemukan")
        segment.status = RoadSegmentStatus.AMAN
        segment.diblokir_manual = False
        segment.alasan = ""
        self.db.flush()
        _refresh_routing_and_twin(self.db, segment.rw_id)
        self.db.commit()
        return ManualBlockResponse(
            segment_id=segment.segment_id,
            status=segment.status,
            diblokir_manual=segment.diblokir_manual,
            rute_dihitung_ulang=True,
        )


def list_reports(db: Session, status: RoadReportStatus) -> list[RoadReport]:
    return db.scalars(
        select(RoadReport)
        .where(RoadReport.status == status)
        .order_by(RoadReport.dibuat_pada.desc())
    ).all()
