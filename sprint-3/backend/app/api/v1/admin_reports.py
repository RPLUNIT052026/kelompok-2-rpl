from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.core.auth import OperatorPrincipal, require_operator
from app.core.database import get_db
from app.models.enums import RoadReportStatus
from app.schemas.report import (
    AdminReportVerificationResponse,
    ReportDecisionRequest,
    ReportQueueResponse,
)
from app.services.report_service import ReportService, list_reports

router = APIRouter(prefix="/admin/reports", tags=["admin-reports"])


@router.get("", response_model=ReportQueueResponse)
def get_report_queue(
    status: RoadReportStatus = Query(default=RoadReportStatus.MENUNGGU_TINJAUAN),
    db: Session = Depends(get_db),
    operator: OperatorPrincipal = Depends(require_operator),
) -> ReportQueueResponse:
    del operator
    return ReportQueueResponse(data=list_reports(db, status))


@router.patch("/{id}", response_model=AdminReportVerificationResponse)
def verify_report(
    payload: ReportDecisionRequest,
    report_id: UUID = Path(alias="id"),
    db: Session = Depends(get_db),
    operator: OperatorPrincipal = Depends(require_operator),
) -> AdminReportVerificationResponse:
    try:
        return ReportService(db).verify_report(report_id, payload.keputusan, operator.id)
    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": str(exc)},
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "CONFLICT", "message": str(exc)},
        ) from exc
