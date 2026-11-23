from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.route import EvacuationResponse
from app.services.routing_engine import RoutingEngine

router = APIRouter(prefix="/routes", tags=["routes"])


@router.get("/evacuation", response_model=EvacuationResponse)
def get_evacuation_routes(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    db: Session = Depends(get_db),
) -> EvacuationResponse:
    try:
        payload = RoutingEngine(db).get_evacuation_routes(lat, lng)
    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": str(exc)},
        ) from exc
    return EvacuationResponse.model_validate(payload)
