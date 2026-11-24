from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import GeoJSON


class DigitalTwinResponse(BaseModel):
    id: UUID
    rw_id: UUID
    zona_bahaya: GeoJSON | None
    tinggi_genangan_cm: float
    ruas_tertutup: int
    estimasi_warga_terdampak: int
    perangkat_aktif: int
    diperbarui_pada: datetime
