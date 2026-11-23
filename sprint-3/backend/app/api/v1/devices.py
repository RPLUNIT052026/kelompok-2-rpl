from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entities import PerangkatWarga, RW
from app.schemas.device import DeviceRegisterRequest, DeviceRegisterResponse

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post(
    "/register",
    response_model=DeviceRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_device(
    payload: DeviceRegisterRequest,
    db: Session = Depends(get_db),
) -> DeviceRegisterResponse:
    rw_exists = db.scalar(select(RW.id).where(RW.id == payload.rw_id))
    if rw_exists is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "RW tidak ditemukan"},
        )

    now = datetime.now(timezone.utc)
    statement = (
        insert(PerangkatWarga)
        .values(
            device_id=payload.device_id,
            rw_id=payload.rw_id,
            fcm_token=payload.fcm_token,
            reputasi=0.5,
            terakhir_aktif=now,
        )
        .on_conflict_do_update(
            index_elements=[PerangkatWarga.device_id],
            set_={
                "rw_id": payload.rw_id,
                "fcm_token": payload.fcm_token,
                "terakhir_aktif": now,
            },
        )
        .returning(PerangkatWarga)
    )
    device = db.execute(statement).scalar_one()
    db.commit()
    return DeviceRegisterResponse(
        device_id=device.device_id,
        rw_id=device.rw_id,
        terdaftar=True,
        reputasi=device.reputasi,
        terakhir_aktif=device.terakhir_aktif,
    )
