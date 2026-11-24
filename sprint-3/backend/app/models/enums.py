from enum import Enum


class LevelBahaya(str, Enum):
    AMAN = "AMAN"
    WASPADA = "WASPADA"
    SIAGA = "SIAGA"
    AWAS = "AWAS"


class RoadSegmentStatus(str, Enum):
    AMAN = "AMAN"
    MENUNGGU_TINJAUAN = "MENUNGGU_TINJAUAN"
    TERTUTUP_SEMENTARA = "TERTUTUP_SEMENTARA"
    TERTUTUP = "TERTUTUP"
    TERTUTUP_MANUAL = "TERTUTUP_MANUAL"


class RoadReportTipe(str, Enum):
    TERTUTUP = "tertutup"
    AMAN = "aman"


class RoadReportStatus(str, Enum):
    MENUNGGU_TINJAUAN = "menunggu_tinjauan"
    TERVERIFIKASI_OTOMATIS = "terverifikasi_otomatis"
    DITERIMA = "diterima"
    DITOLAK = "ditolak"
