from datetime import datetime, timedelta
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import RoadReportStatus, RoadReportTipe, RoadSegmentStatus


class ReportCreateRequest(BaseModel):
    device_id: str = Field(min_length=1, max_length=128)
    segment_id: UUID
    tipe: RoadReportTipe
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    catatan: str = ""
    dibuat_pada: datetime

    @field_validator("dibuat_pada")
    @classmethod
    def require_utc_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() != timedelta(0):
            raise ValueError("dibuat_pada harus memiliki zona waktu UTC")
        return value


class ReportCreateResponse(BaseModel):
    id: UUID
    segment_id: UUID
    skor_kepercayaan: float
    status: RoadReportStatus
    road_segment_status: RoadSegmentStatus
    rute_dihitung_ulang: bool


class ReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    segment_id: UUID
    device_id: str
    tipe: RoadReportTipe
    lat: float
    lng: float
    catatan: str
    skor_kepercayaan: float
    status: RoadReportStatus
    diverifikasi_oleh: UUID | None
    dibuat_pada: datetime


class ReportQueueResponse(BaseModel):
    data: list[ReportItem]


class ReportDecisionRequest(BaseModel):
    keputusan: Literal["diterima", "ditolak"]


class AdminReportVerificationResponse(BaseModel):
    id: UUID
    status: RoadReportStatus
    road_segment_status: RoadSegmentStatus
    reputasi_diperbarui: bool
    rute_dihitung_ulang: bool
