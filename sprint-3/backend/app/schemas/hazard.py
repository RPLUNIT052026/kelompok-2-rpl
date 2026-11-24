from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import LevelBahaya
from app.schemas.common import GeoJSON


class RWHazardInfo(BaseModel):
    id: UUID
    nama_rw: str
    batas_wilayah: GeoJSON
    titik_kumpul: GeoJSON


class HazardItem(BaseModel):
    id: UUID
    rw_id: UUID
    sumber: str
    jenis: str
    level_bahaya: LevelBahaya
    tingkat_bahaya: float
    geometri: GeoJSON
    waktu_data: datetime
    terverifikasi: bool


class HazardsResponse(BaseModel):
    rw: RWHazardInfo
    data_diperbarui: datetime
    data_kedaluwarsa: bool
    hazards: list[HazardItem]
