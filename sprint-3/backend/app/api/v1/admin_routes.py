from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping
from shapely.geometry.base import BaseGeometry
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import OperatorPrincipal, require_operator
from app.core.database import get_db
from app.models.entities import RW, RoadSegment
from app.schemas.admin_route import (
    ManualBlockRequest,
    ManualBlockResponse,
    RoadSegmentListResponse,
)
from app.services.report_service import ReportService

router = APIRouter(prefix="/admin/routes", tags=["admin-routes"])


@router.get("/segments", response_model=RoadSegmentListResponse)
def list_route_segments(
    rw: UUID = Query(...),
    db: Session = Depends(get_db),
    operator: OperatorPrincipal = Depends(require_operator),
) -> RoadSegmentListResponse:
    del operator
    if db.get(RW, rw) is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "RW tidak ditemukan"},
        )

    segments = db.scalars(
        select(RoadSegment)
        .where(RoadSegment.rw_id == rw)
        .order_by(RoadSegment.segment_id)
    ).all()
    return RoadSegmentListResponse(
        data=[
            {
                "segment_id": segment.segment_id,
                "rw_id": segment.rw_id,
                "geometri": mapping(
                    segment.geometri
                    if isinstance(segment.geometri, BaseGeometry)
                    else to_shape(segment.geometri)
                ),
                "panjang_m": segment.panjang_m,
                "kecepatan_rata_rata_mps": segment.kecepatan_rata_rata_mps,
                "kapasitas_maks": segment.kapasitas_maks,
                "pengguna_aktif": segment.pengguna_aktif,
                "status": segment.status,
                "diblokir_manual": segment.diblokir_manual,
                "alasan": segment.alasan,
            }
            for segment in segments
        ]
    )


@router.post("/block", response_model=ManualBlockResponse)
def block_route(
    payload: ManualBlockRequest,
    db: Session = Depends(get_db),
    operator: OperatorPrincipal = Depends(require_operator),
) -> ManualBlockResponse:
    del operator
    try:
        return ReportService(db).block_segment(payload.segment_id, payload.alasan)
    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": str(exc)},
        ) from exc


@router.delete("/block/{segment_id}", response_model=ManualBlockResponse)
def unblock_route(
    segment_id: UUID,
    db: Session = Depends(get_db),
    operator: OperatorPrincipal = Depends(require_operator),
) -> ManualBlockResponse:
    del operator
    try:
        return ReportService(db).unblock_segment(segment_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": str(exc)},
        ) from exc
