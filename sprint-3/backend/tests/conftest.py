import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from geoalchemy2.shape import from_shape
from shapely.geometry import Point, Polygon
from sqlalchemy.dialects.postgresql import dialect

from app.core.database import get_db
from app.core.config import Settings
from app.core.redis_client import get_redis
from app.main import app
from app.models.entities import Hazard, PerangkatWarga, RW

RW_ID = uuid.UUID("3f0c6b1e-0000-0000-0000-000000000001")
HAZARD_ID = uuid.UUID("a1b2c3d4-0000-0000-0000-000000000010")


def sample_rw() -> SimpleNamespace:
    return SimpleNamespace(
        id=RW_ID,
        nama_rw="RW 05 — Gampong Jawa, Langsa Kota",
        batas_wilayah=from_shape(
            Polygon(
                [
                    (97.958, 4.462),
                    (97.970, 4.462),
                    (97.970, 4.476),
                    (97.958, 4.476),
                    (97.958, 4.462),
                ]
            ),
            srid=4326,
        ),
        titik_kumpul=from_shape(Point(97.9664134, 4.4708906), srid=4326),
        data_diperbarui=datetime(2026, 9, 29, 8, 0, tzinfo=timezone.utc),
        data_kedaluwarsa=False,
    )


def sample_hazard() -> SimpleNamespace:
    return SimpleNamespace(
        id=HAZARD_ID,
        rw_id=RW_ID,
        sumber="BMKG",
        jenis="cuaca_ekstrem",
        level_bahaya="SIAGA",
        tingkat_bahaya=3.5,
        geometri=from_shape(
            Polygon(
                [
                    (97.9666, 4.4693),
                    (97.9671, 4.4693),
                    (97.9671, 4.4696),
                    (97.9666, 4.4696),
                    (97.9666, 4.4693),
                ]
            ),
            srid=4326,
        ),
        waktu_data=datetime(2026, 9, 29, 8, 0, tzinfo=timezone.utc),
        terverifikasi=False,
    )


class FakeRedis:
    def __init__(self):
        self.data: dict[str, str] = {}

    def get(self, key: str):
        return self.data.get(key)

    def set(self, key: str, value: str):
        self.data[key] = value
        return True

    def ping(self):
        return True


class _Result:
    def __init__(self, value=None):
        self.value = value

    def scalar_one(self):
        return self.value


class _ScalarList:
    def __init__(self, values):
        self.values = values

    def all(self):
        return self.values


class FakeSession:
    def __init__(self):
        self.rw = sample_rw()
        self.rw_exists = True
        self.hazards = [sample_hazard()]
        self.devices: dict[str, SimpleNamespace] = {}
        self.merged: list[object] = []
        self.commits = 0

    def get(self, model, key):
        if model is RW:
            return self.rw if self.rw_exists and key == self.rw.id else None
        if model is PerangkatWarga:
            return self.devices.get(key)
        if model is Hazard:
            return next((row for row in self.hazards if row.id == key), None)
        return None

    def scalar(self, statement):
        return self.rw if self.rw_exists else None

    def scalars(self, statement):
        sql = str(statement).lower()
        if "from hazard" in sql:
            return _ScalarList(self.hazards)
        if "from rw" in sql:
            return _ScalarList([self.rw] if self.rw_exists else [])
        return _ScalarList([])

    def execute(self, statement):
        sql = str(statement).lower()
        if "insert into perangkat_warga" in sql:
            params = statement.compile(dialect=dialect()).params
            device_id = params["device_id"]
            rw_id = params["rw_id"]
            token = params["fcm_token"]
            active_at = params["terakhir_aktif"]
            existing = self.devices.get(device_id)
            reputation = existing.reputasi if existing else params["reputasi"]
            device = SimpleNamespace(
                device_id=device_id,
                rw_id=rw_id,
                fcm_token=token,
                reputasi=reputation,
                terakhir_aktif=active_at,
            )
            self.devices[device_id] = device
            return _Result(device)
        return _Result()

    def merge(self, value):
        self.merged.append(value)
        return value

    def commit(self):
        self.commits += 1


state = SimpleNamespace(db=FakeSession(), redis=FakeRedis())


def _override_db():
    return state.db


def _override_redis():
    return state.redis


app.dependency_overrides[get_db] = _override_db
app.dependency_overrides[get_redis] = _override_redis


@pytest.fixture(scope="session")
def api_client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def api_state(api_client):
    state.db = FakeSession()
    state.redis = FakeRedis()
    return state


@pytest.fixture
def operator_headers(monkeypatch):
    from app.core import auth

    operator_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    settings = Settings(
        operator_api_token="test-operator-token",
        operator_user_id=operator_id,
        auth_jwt_secret="test-jwt-secret",
    )
    monkeypatch.setattr(auth, "get_settings", lambda: settings)
    return {"Authorization": "Bearer test-operator-token"}
