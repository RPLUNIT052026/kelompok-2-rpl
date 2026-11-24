from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import RoadSegmentStatus
from app.schemas.common import GeoJSON


class RouteOrigin(BaseModel):
    lat: float
    lng: float


class RouteSegmentResponse(BaseModel):
    segment_id: UUID
    rw_id: UUID
    geometri: GeoJSON
    panjang_m: float
    kecepatan_rata_rata_mps: float
    kapasitas_maks: int
    pengguna_aktif: int
    status: RoadSegmentStatus
    diblokir_manual: bool
    alasan: str


class EvacuationRouteResponse(BaseModel):
    id: str
    rw_id: UUID
    utama: bool
    jarak_m: int
    estimasi_menit: int
    status: RoadSegmentStatus
    beban_persen: float
    segmen_dilalui: list[RouteSegmentResponse]
    geometri: GeoJSON


class EvacuationResponse(BaseModel):
    asal: RouteOrigin
    dihitung_pada: datetime
    evakuasi_vertikal: bool
    pesan_darurat: str | None
    alert_sar: bool
    rute: list[EvacuationRouteResponse]
