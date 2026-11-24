from typing import Any

from pydantic import BaseModel, ConfigDict


class GeoJSON(BaseModel):
    type: str
    coordinates: Any


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[Any]


class ErrorResponse(BaseModel):
    error: ErrorDetail


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
