from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.redis_client import get_redis
from app.models.entities import Hazard, RW
from app.models.enums import LevelBahaya
from app.schemas.hazard import HazardsResponse

router = APIRouter(prefix="/hazards", tags=["hazards"])


def _geojson(geometry: object) -> dict:
    return mapping(to_shape(geometry))


def _cache_flag(redis: object) -> bool:
    value = redis.get("cache:meta:data_kedaluwarsa")
    return str(value).lower() == "true"


@router.get("", response_model=HazardsResponse)
def get_hazards(
    rw: UUID = Query(...),
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
) -> HazardsResponse:
    rw_record = db.get(RW, rw)
    if rw_record is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "RW tidak ditemukan"},
        )
    hazards = db.scalars(
        select(Hazard)
        .where(
            Hazard.rw_id == rw,
            Hazard.level_bahaya.in_(
                [LevelBahaya.WASPADA, LevelBahaya.SIAGA, LevelBahaya.AWAS]
            ),
        )
        .order_by(Hazard.waktu_data.desc())
    ).all()
    return HazardsResponse(
        rw={
            "id": rw_record.id,
            "nama_rw": rw_record.nama_rw,
            "batas_wilayah": _geojson(rw_record.batas_wilayah),
            "titik_kumpul": _geojson(rw_record.titik_kumpul),
        },
        data_diperbarui=rw_record.data_diperbarui,
        data_kedaluwarsa=rw_record.data_kedaluwarsa or _cache_flag(redis),
        hazards=[
            {
                "id": hazard.id,
                "rw_id": hazard.rw_id,
                "sumber": hazard.sumber,
                "jenis": hazard.jenis,
                "level_bahaya": hazard.level_bahaya,
                "tingkat_bahaya": hazard.tingkat_bahaya,
                "geometri": _geojson(hazard.geometri),
                "waktu_data": hazard.waktu_data,
                "terverifikasi": hazard.terverifikasi,
            }
            for hazard in hazards
        ],
    )
