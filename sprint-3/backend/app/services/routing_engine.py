import itertools
import logging
import math
import uuid
from datetime import datetime, timezone
from typing import Any

import networkx as nx
from geoalchemy2.shape import to_shape
from shapely.geometry import LineString, mapping
from shapely.geometry.base import BaseGeometry
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.entities import EvacuationRoute, Hazard, RW, RoadSegment
from app.models.enums import LevelBahaya, RoadSegmentStatus

logger = logging.getLogger(__name__)
EMERGENCY_MESSAGE = "Tidak ada rute aman. Lakukan evakuasi vertikal ke lokasi kokoh terdekat."


def _shape(geometry: Any) -> BaseGeometry:
    if isinstance(geometry, BaseGeometry):
        return geometry
    return to_shape(geometry)


def _value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _node(point: tuple[float, float]) -> tuple[float, float]:
    return round(float(point[0]), 6), round(float(point[1]), 6)


class RoutingEngine:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def invalidate_routes(db: Session, rw_id: uuid.UUID) -> None:
        db.execute(delete(EvacuationRoute).where(EvacuationRoute.rw_id == rw_id))

    def get_evacuation_routes(self, lat: float, lng: float) -> dict[str, Any]:
        point = func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326)
        rw = self.db.scalar(select(RW).where(func.ST_Contains(RW.batas_wilayah, point)))
        if rw is None:
            rw = self.db.scalar(
                select(RW).order_by(func.ST_Distance(RW.batas_wilayah, point)).limit(1)
            )
        if rw is None:
            raise LookupError("RW tidak ditemukan untuk lokasi yang diberikan")

        impacted_rows = self.db.scalars(
            select(RoadSegment.segment_id)
            .join(Hazard, func.ST_Intersects(RoadSegment.geometri, Hazard.geometri))
            .where(
                RoadSegment.rw_id == rw.id,
                Hazard.rw_id == rw.id,
                Hazard.level_bahaya.in_([LevelBahaya.SIAGA, LevelBahaya.AWAS]),
            )
        ).all()
        segments = self.db.scalars(
            select(RoadSegment).where(RoadSegment.rw_id == rw.id)
        ).all()
        impacted_ids = {str(segment_id) for segment_id in impacted_rows}

        safe_segments = [
            segment
            for segment in segments
            if str(segment.segment_id) not in impacted_ids
            and _value(segment.status) == RoadSegmentStatus.AMAN.value
            and not segment.diblokir_manual
        ]
        candidates = self.calculate_k_shortest_paths(
            origin=(lng, lat),
            destination=_shape(rw.titik_kumpul).coords[0],
            segments=safe_segments,
            rw_id=rw.id,
            rw_name=rw.nama_rw,
        )
        if not candidates:
            return self._vertical_evacuation(lat, lng)

        main_index = 0
        if any(
            segment.pengguna_aktif > 0.8 * segment.kapasitas_maks
            for segment in candidates[0]["segments"]
        ):
            main_index = min(
                range(len(candidates)),
                key=lambda index: candidates[index]["beban_persen"],
            )

        for index, candidate in enumerate(candidates):
            candidate["utama"] = index == main_index
        for segment in candidates[main_index]["segments"]:
            segment.pengguna_aktif += 1
        self.db.commit()

        return {
            "asal": {"lat": lat, "lng": lng},
            "dihitung_pada": datetime.now(timezone.utc),
            "evakuasi_vertikal": False,
            "pesan_darurat": None,
            "alert_sar": False,
            "rute": [self._route_response(rw.id, route) for route in candidates],
        }

    def calculate_k_shortest_paths(
        self,
        origin: tuple[float, float],
        destination: tuple[float, float],
        segments: list[RoadSegment],
        rw_id: uuid.UUID,
        rw_name: str,
        k: int = 3,
    ) -> list[dict[str, Any]]:
        graph = nx.Graph()
        for segment in segments:
            geometry = _shape(segment.geometri)
            coordinates = [_node(point[:2]) for point in geometry.coords]
            start, end = coordinates[0], coordinates[-1]
            graph.add_edge(
                start,
                end,
                weight=segment.panjang_m / segment.kecepatan_rata_rata_mps,
                segment=segment,
                coordinates=coordinates,
            )
        if graph.number_of_edges() == 0:
            return []

        origin_node = self._nearest_node(graph, _node(origin))
        destination_node = self._nearest_node(graph, _node(destination))
        if origin_node != _node(origin):
            graph.add_edge(
                ("origin", _node(origin)),
                origin_node,
                weight=self._connector_cost(_node(origin), origin_node),
                segment=None,
                coordinates=[_node(origin), origin_node],
            )
            origin_node = ("origin", _node(origin))
        if origin_node == destination_node:
            return []

        prefix = rw_name.split()[-1] if rw_name.split() else str(rw_id)[:8]
        routes: list[dict[str, Any]] = []
        try:
            paths = nx.shortest_simple_paths(
                graph, origin_node, destination_node, weight="weight"
            )
            for path_number, path in enumerate(itertools.islice(paths, k), start=1):
                route_segments: list[RoadSegment] = []
                route_coordinates: list[tuple[float, float]] = []
                total_cost = 0.0
                for start, end in zip(path, path[1:]):
                    edge = graph.get_edge_data(start, end)
                    total_cost += edge["weight"]
                    route_coordinates.extend(
                        self._oriented_coordinates(edge, start, end)
                    )
                    segment = edge["segment"]
                    if segment is not None:
                        route_segments.append(segment)
                if not route_segments or len(route_coordinates) < 2:
                    continue
                route_coordinates = self._deduplicate_coordinates(route_coordinates)
                line = LineString(route_coordinates)
                distance = sum(segment.panjang_m for segment in route_segments)
                max_load = max(
                    (segment.pengguna_aktif / segment.kapasitas_maks) * 100
                    for segment in route_segments
                )
                route_id = f"R-{prefix}" if path_number == 1 else f"R-{prefix}-{path_number}"
                routes.append(
                    {
                        "id": route_id,
                        "rw_id": rw_id,
                        "utama": False,
                        "jarak_m": int(round(distance)),
                        "estimasi_menit": int(math.ceil(total_cost / 60)),
                        "status": RoadSegmentStatus.AMAN,
                        "beban_persen": round(max_load, 1),
                        "segments": route_segments,
                        "geometri": mapping(line),
                    }
                )
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            logger.info("No safe route found", extra={"rw_id": str(rw_id)})
        return routes

    @staticmethod
    def _nearest_node(graph: nx.Graph, point: tuple[float, float]) -> Any:
        return min(
            graph.nodes,
            key=lambda node: (float(node[0]) - point[0]) ** 2 + (float(node[1]) - point[1]) ** 2,
        )

    @staticmethod
    def _connector_cost(start: tuple[float, float], end: tuple[float, float]) -> float:
        distance_m = math.hypot((end[0] - start[0]) * 111_320, (end[1] - start[1]) * 110_540)
        return distance_m / 1.4

    @staticmethod
    def _oriented_coordinates(
        edge: dict[str, Any], start: Any, end: Any
    ) -> list[tuple[float, float]]:
        coordinates = edge["coordinates"]
        if isinstance(start, tuple) and start and start[0] == "origin":
            return coordinates
        if isinstance(end, tuple) and end and end[0] == "origin":
            return list(reversed(coordinates))
        if _node(start) == coordinates[-1] and _node(end) == coordinates[0]:
            return list(reversed(coordinates))
        return coordinates

    @staticmethod
    def _deduplicate_coordinates(
        coordinates: list[tuple[float, float]],
    ) -> list[tuple[float, float]]:
        result: list[tuple[float, float]] = []
        for point in coordinates:
            if not result or point != result[-1]:
                result.append(point)
        return result

    @staticmethod
    def _vertical_evacuation(lat: float, lng: float) -> dict[str, Any]:
        return {
            "asal": {"lat": lat, "lng": lng},
            "dihitung_pada": datetime.now(timezone.utc),
            "evakuasi_vertikal": True,
            "pesan_darurat": EMERGENCY_MESSAGE,
            "alert_sar": True,
            "rute": [],
        }

    @staticmethod
    def _route_response(rw_id: uuid.UUID, route: dict[str, Any]) -> dict[str, Any]:
        segments = []
        for segment in route["segments"]:
            segments.append(
                {
                    "segment_id": segment.segment_id,
                    "rw_id": segment.rw_id,
                    "geometri": mapping(_shape(segment.geometri)),
                    "panjang_m": segment.panjang_m,
                    "kecepatan_rata_rata_mps": segment.kecepatan_rata_rata_mps,
                    "kapasitas_maks": segment.kapasitas_maks,
                    "pengguna_aktif": segment.pengguna_aktif,
                    "status": segment.status,
                    "diblokir_manual": segment.diblokir_manual,
                    "alasan": segment.alasan,
                }
            )
        return {
            "id": route["id"],
            "rw_id": rw_id,
            "utama": route["utama"],
            "jarak_m": route["jarak_m"],
            "estimasi_menit": route["estimasi_menit"],
            "status": route["status"],
            "beban_persen": route["beban_persen"],
            "segmen_dilalui": segments,
            "geometri": route["geometri"],
        }
