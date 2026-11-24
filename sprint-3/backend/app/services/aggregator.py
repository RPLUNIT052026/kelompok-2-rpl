import asyncio
import json
import logging
import math
import uuid
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from typing import Any

import httpx
from geoalchemy2.shape import from_shape
from shapely.errors import GEOSException
from shapely.geometry import Point, Polygon, shape
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models.entities import Hazard, RW
from app.models.enums import LevelBahaya
from app.services.notification_stub import trigger_emergency_hooks

logger = logging.getLogger(__name__)


class SourceUnavailable(Exception):
    pass


class DataAggregator:
    def __init__(
        self,
        db: Session,
        redis: Any,
        settings: Settings | None = None,
        http_client: httpx.AsyncClient | None = None,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ):
        self.db = db
        self.redis = redis
        self.settings = settings or get_settings()
        self.http_client = http_client
        self.sleep = sleep
        self.max_retry = self.settings.http_retries

    async def fetchBMKG(self) -> dict[str, Any]:
        earthquake, weather = await asyncio.gather(
            self._fetch_json(self.settings.bmkg_gempa_url),
            self._fetch_json(
                self.settings.bmkg_cuaca_url,
                params={"adm4": self.settings.bmkg_adm4},
            ),
        )
        return {"earthquake": earthquake, "weather": weather}

    async def fetchUSGS(self) -> dict[str, Any]:
        return await self._fetch_json(self.settings.usgs_url)

    async def _fetch_json(
        self, url: str, params: dict[str, str] | None = None
    ) -> dict[str, Any]:
        last_error: Exception | None = None
        for retry_count in range(self.max_retry):
            try:
                if self.http_client is not None:
                    response = await self.http_client.get(url, params=params)
                else:
                    async with httpx.AsyncClient(timeout=self.settings.http_timeout) as client:
                        response = await client.get(url, params=params)
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict):
                    raise ValueError("Sumber data harus mengembalikan objek JSON")
                return payload
            except (httpx.HTTPError, ValueError) as exc:
                last_error = exc
                await self.sleep(2**retry_count)
        raise SourceUnavailable(f"Gagal mengambil data dari {url}") from last_error

    def normalizePayload(self, source: str, raw_payload: dict[str, Any]) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        if isinstance(raw_payload.get("hazards"), list):
            raw_entries = raw_payload["hazards"]
            for index, item in enumerate(raw_entries):
                normalized = self._normalize_entry(source, item, str(index))
                if normalized is not None:
                    entries.append(normalized)
            return entries

        if source == "usgs":
            features = raw_payload.get("features", [])
            if not isinstance(features, list):
                self._warn_invalid(source)
                return entries
            for feature in features:
                if not isinstance(feature, dict):
                    self._warn_invalid(source)
                    continue
                properties = feature.get("properties") or {}
                geometry = feature.get("geometry") or {}
                if not isinstance(properties, dict) or not isinstance(geometry, dict):
                    self._warn_invalid(source)
                    continue
                coordinates = geometry.get("coordinates")
                if not isinstance(coordinates, list) or len(coordinates) < 2:
                    self._warn_invalid(source)
                    continue
                entry = {
                    "source_id": feature.get("id"),
                    "jenis": "gempa",
                    "tingkat_bahaya": properties.get("mag"),
                    "waktu_data": properties.get("time"),
                    "lat": coordinates[1],
                    "lng": coordinates[0],
                    "tsunami": properties.get("tsunami", 0),
                    "place": properties.get("place", ""),
                }
                normalized = self._normalize_entry(source, entry, str(len(entries)))
                if normalized is not None:
                    entries.append(normalized)
            return entries

        if source == "bmkg":
            earthquake = raw_payload.get("earthquake", raw_payload)
            if not isinstance(earthquake, dict):
                self._warn_invalid(source)
                return entries
            earthquake_info = earthquake.get("Infogempa") or {}
            if not isinstance(earthquake_info, dict):
                self._warn_invalid(source)
                earthquake_info = {}
            quake = earthquake_info.get("gempa") or earthquake.get("gempa") or earthquake.get("quake")
            if isinstance(quake, dict):
                normalized = self._normalize_bmkg_quake(quake)
                if normalized is not None:
                    entries.append(normalized)
            weather = raw_payload.get("weather", {})
            if not isinstance(weather, dict):
                self._warn_invalid(source)
                return entries
            for index, item in enumerate(self._weather_entries(weather)):
                if not item.get("lokasi") and weather.get("lokasi"):
                    item = {**item, "lokasi": weather["lokasi"]}
                normalized = self._normalize_bmkg_weather(item, index)
                if normalized is not None:
                    entries.append(normalized)
            return entries

        logger.warning("Unsupported aggregator source: %s", source)
        return entries

    def _normalize_entry(
        self, source: str, item: dict[str, Any], fallback_id: str
    ) -> dict[str, Any] | None:
        try:
            lat = float(item["lat"])
            lng = float(item["lng"])
            severity = float(item["tingkat_bahaya"])
            if not math.isfinite(severity) or severity < 0:
                raise ValueError("severity must be finite and non-negative")
            if not math.isfinite(lat) or not math.isfinite(lng) or not -90 <= lat <= 90 or not -180 <= lng <= 180:
                raise ValueError("coordinates outside WGS 84 range")
            geometry = self._hazard_polygon(item.get("geometri"), lat, lng)
            timestamp = self._parse_timestamp(item.get("waktu_data"))
            return {
                "source_id": str(item.get("source_id") or fallback_id),
                "sumber": source.upper(),
                "jenis": str(item.get("jenis") or "bahaya"),
                "level_bahaya": self._severity_level(
                    severity,
                    bool(item.get("tsunami")),
                    str(item.get("jenis") or ""),
                    str(item.get("deskripsi") or ""),
                ),
                "tingkat_bahaya": severity,
                "geometri": geometry,
                "waktu_data": timestamp,
            }
        except (GEOSException, KeyError, TypeError, ValueError, OverflowError):
            self._warn_invalid(source)
            return None

    def _normalize_bmkg_quake(self, quake: dict[str, Any]) -> dict[str, Any] | None:
        coordinates = quake.get("Coordinates") or quake.get("coordinates")
        lat: float | None = None
        lng: float | None = None
        if isinstance(coordinates, str) and "," in coordinates:
            first, second = coordinates.split(",", 1)
            lat, lng = self._coordinate(first), self._coordinate(second)
        if lat is None:
            lat = self._coordinate(quake.get("Lintang"))
        if lng is None:
            lng = self._coordinate(quake.get("Bujur"))
        severity = quake.get("Magnitude") or quake.get("magnitude")
        if lat is None or lng is None or severity is None:
            self._warn_invalid("bmkg")
            return None
        try:
            timestamp = self._parse_bmkg_timestamp(quake)
        except ValueError:
            self._warn_invalid("bmkg")
            return None
        potential = str(quake.get("Potensi") or "").lower()
        tsunami = "tsunami" in potential and "tidak berpotensi" not in potential
        return self._normalize_entry(
            "bmkg",
            {
                "source_id": (
                    quake.get("DateTime")
                    or f"{quake.get('Tanggal', '')}-{quake.get('Jam', '')}".strip("-")
                    or timestamp.isoformat()
                ),
                "jenis": "gempa",
                "tingkat_bahaya": severity,
                "lat": lat,
                "lng": lng,
                "waktu_data": timestamp,
                "tsunami": tsunami,
            },
            "gempa",
        )

    def _normalize_bmkg_weather(self, item: dict[str, Any], index: int) -> dict[str, Any] | None:
        location = item.get("lokasi") or item.get("location") or item
        if not isinstance(location, dict):
            self._warn_invalid("bmkg")
            return None
        lat = self._coordinate(location.get("lat"))
        lng = self._coordinate(location.get("lon") or location.get("lng"))
        if lat is None or lng is None:
            self._warn_invalid("bmkg")
            return None
        forecast = item.get("cuaca") or item.get("weather") or []
        if isinstance(forecast, list):
            forecast = [entry for group in forecast for entry in (group if isinstance(group, list) else [group])]
        rainfall = max(
            (self._nonnegative_number(entry.get("tp")) for entry in forecast if isinstance(entry, dict)),
            default=0.0,
        )
        description = " ".join(
            str(entry.get("weather_desc") or "")
            for entry in forecast
            if isinstance(entry, dict)
        )
        return self._normalize_entry(
            "bmkg",
            {
                "source_id": f"cuaca-{location.get('adm4', index)}",
                "jenis": "curah_hujan",
                "tingkat_bahaya": rainfall,
                "deskripsi": description,
                "lat": lat,
                "lng": lng,
                "waktu_data": datetime.now(timezone.utc),
            },
            f"cuaca-{index}",
        )

    @staticmethod
    def _weather_entries(payload: dict[str, Any]) -> list[dict[str, Any]]:
        if not isinstance(payload, dict):
            return []
        entries = payload.get("data", [])
        if not isinstance(entries, list):
            return []
        return [entry for entry in entries if isinstance(entry, dict)]

    def _parse_bmkg_timestamp(self, quake: dict[str, Any]) -> datetime:
        value = quake.get("DateTime")
        if value:
            try:
                return self._parse_timestamp(value)
            except (TypeError, ValueError):
                pass

        date_text = str(quake.get("Tanggal") or quake.get("Date") or "").strip()
        time_text = str(quake.get("Jam") or "").strip()
        time_text = time_text.replace("WIB", "").replace("WITA", "").replace("WIT", "").strip()
        combined = f"{date_text} {time_text}".strip()
        for date_format in (
            "%d %b %Y %H:%M:%S",
            "%d %B %Y %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%d %b %Y",
            "%d %B %Y",
            "%Y-%m-%d",
        ):
            try:
                parsed = datetime.strptime(combined, date_format)
                return parsed.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        if not date_text:
            return datetime.now(timezone.utc)
        raise ValueError(f"Unrecognized BMKG timestamp: {combined}")

    @staticmethod
    def _coordinate(value: Any) -> float | None:
        if value is None:
            return None
        text = str(value).strip().upper()
        direction = text[-2:] if len(text) > 2 and text[-2:] in {"LS", "LU", "BT", "BB"} else ""
        number = text[:-2].strip() if direction else text
        try:
            result = float(number)
        except ValueError:
            return None
        if direction in {"LS", "BB"}:
            result = -abs(result)
        elif direction in {"LU", "BT"}:
            result = abs(result)
        return result

    @staticmethod
    def _nonnegative_number(value: Any) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return 0.0
        return number if math.isfinite(number) and number >= 0 else 0.0

    @staticmethod
    def _parse_timestamp(value: Any) -> datetime:
        if isinstance(value, datetime):
            timestamp = value
        elif isinstance(value, (int, float)):
            timestamp = datetime.fromtimestamp(value / 1000 if value > 10**12 else value, timezone.utc)
        else:
            timestamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        return timestamp.astimezone(timezone.utc)

    @staticmethod
    def _severity_level(
        severity: float, tsunami: bool, kind: str, description: str = ""
    ) -> LevelBahaya:
        if tsunami:
            return LevelBahaya.SIAGA
        if kind == "curah_hujan":
            description = description.lower()
            if severity >= 50 or "hujan lebat" in description or "hujan petir" in description:
                return LevelBahaya.AWAS
            if severity >= 20:
                return LevelBahaya.SIAGA
            if severity >= 5 or "hujan sedang" in description:
                return LevelBahaya.WASPADA
            return LevelBahaya.AMAN
        if severity >= 7:
            return LevelBahaya.AWAS
        if severity >= 6.5:
            return LevelBahaya.SIAGA
        if severity >= 5:
            return LevelBahaya.WASPADA
        return LevelBahaya.AMAN

    @staticmethod
    def _hazard_polygon(geometry: Any, lat: float, lng: float) -> Polygon:
        if isinstance(geometry, dict):
            parsed = shape(geometry)
            if isinstance(parsed, Polygon):
                return parsed
            if isinstance(parsed, Point):
                return parsed.buffer(0.001)
        return Point(lng, lat).buffer(0.001)

    @staticmethod
    def _warn_invalid(source: str) -> None:
        logger.warning("Discarded invalid %s hazard payload entry", source.upper())

    async def fallbackToCache(self, source: str) -> dict[str, Any] | None:
        cached = self.redis.get(f"cache:{source}:payload")
        for rw in self.db.scalars(select(RW)).all():
            rw.data_kedaluwarsa = True
        self.db.commit()
        self.redis.set("cache:meta:data_kedaluwarsa", "true")
        self.redis.set(f"cache:{source}:status", "degraded")
        self.redis.set("aggregator:status", "degraded")
        if cached is None:
            return None
        try:
            return json.loads(cached)
        except json.JSONDecodeError:
            logger.warning("Ignoring malformed cached %s payload", source.upper())
            return None

    async def run_cycle(self) -> dict[str, str]:
        statuses: dict[str, str] = {}
        for source in ("bmkg", "usgs"):
            try:
                payload = await (self.fetchBMKG() if source == "bmkg" else self.fetchUSGS())
            except SourceUnavailable:
                await self.fallbackToCache(source)
                statuses[source] = "degraded"
                continue
            self._persist_payload(source, payload)
            statuses[source] = "ok"

        degraded = any(status != "ok" for status in statuses.values())
        self.redis.set("aggregator:status", "degraded" if degraded else "ok")
        self.redis.set("cache:meta:data_kedaluwarsa", "true" if degraded else "false")
        self.db.execute(
            update(RW).values(data_kedaluwarsa=degraded)
        )
        if not degraded:
            self.db.execute(update(RW).values(data_diperbarui=datetime.now(timezone.utc)))
        self.db.commit()
        return statuses

    def _persist_payload(self, source: str, payload: dict[str, Any]) -> None:
        hazards = self.normalizePayload(source, payload)
        for item in hazards:
            rw = self.db.scalar(
                select(RW).where(
                    func.ST_Intersects(RW.batas_wilayah, from_shape(item["geometri"], srid=4326))
                )
            )
            if rw is None:
                logger.warning("No RW area intersects %s hazard %s", source.upper(), item["source_id"])
                continue
            hazard_id = uuid.uuid5(uuid.NAMESPACE_URL, f"{source}:{item['source_id']}")
            hazard = Hazard(
                id=hazard_id,
                rw_id=rw.id,
                sumber=item["sumber"],
                jenis=item["jenis"],
                level_bahaya=item["level_bahaya"],
                tingkat_bahaya=item["tingkat_bahaya"],
                geometri=from_shape(item["geometri"], srid=4326),
                waktu_data=item["waktu_data"],
                terverifikasi=False,
            )
            self.db.merge(hazard)
            if item["level_bahaya"] in (LevelBahaya.SIAGA, LevelBahaya.AWAS):
                trigger_emergency_hooks(rw.id, hazard)
        now = datetime.now(timezone.utc)
        self.db.execute(
            update(RW).values(data_diperbarui=now, data_kedaluwarsa=False)
        )
        self.db.commit()
        self.redis.set(f"cache:{source}:payload", json.dumps(payload, default=str))
        self.redis.set(f"cache:{source}:updated_at", now.isoformat().replace("+00:00", "Z"))
        self.redis.set(f"cache:{source}:status", "ok")
