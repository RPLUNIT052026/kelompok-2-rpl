from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DeviceRegisterRequest(BaseModel):
    device_id: str = Field(min_length=1, max_length=128)
    fcm_token: str = Field(min_length=1)
    rw_id: UUID


class DeviceRegisterResponse(BaseModel):
    device_id: str
    rw_id: UUID
    terdaftar: bool
    reputasi: float
    terakhir_aktif: datetime
