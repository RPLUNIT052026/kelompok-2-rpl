from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import RoadSegmentStatus
from app.schemas.route import RouteSegmentResponse


class ManualBlockRequest(BaseModel):
    segment_id: UUID
    alasan: str = Field(min_length=1, max_length=1000)


class ManualBlockResponse(BaseModel):
    segment_id: UUID
    status: RoadSegmentStatus
    diblokir_manual: bool
    rute_dihitung_ulang: bool


class RoadSegmentListResponse(BaseModel):
    data: list[RouteSegmentResponse]
