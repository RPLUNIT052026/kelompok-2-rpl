from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.report import ReportCreateRequest, ReportCreateResponse
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportCreateResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    payload: ReportCreateRequest,
    db: Session = Depends(get_db),
) -> ReportCreateResponse:
    try:
        return ReportService(db).submit_report(payload)
    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": str(exc)},
        ) from exc
