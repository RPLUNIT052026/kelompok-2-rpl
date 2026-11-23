from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import OperatorPrincipal, require_operator
from app.core.database import get_db
from app.schemas.twin import DigitalTwinResponse
from app.services.digital_twin_service import DigitalTwinService

router = APIRouter(prefix="/twin", tags=["digital-twin"])


@router.get("/{rw_id}", response_model=DigitalTwinResponse)
def get_digital_twin(
    rw_id: UUID,
    db: Session = Depends(get_db),
    operator: OperatorPrincipal = Depends(require_operator),
) -> DigitalTwinResponse:
    del operator
    try:
        return DigitalTwinService(db).refresh_snapshot(rw_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": str(exc)},
        ) from exc
