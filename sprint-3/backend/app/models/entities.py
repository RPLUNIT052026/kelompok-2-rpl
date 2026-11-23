import uuid
from datetime import datetime, timezone

from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    Column,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.models.enums import LevelBahaya, RoadReportStatus, RoadReportTipe, RoadSegmentStatus


class Base(DeclarativeBase):
    pass


level_bahaya_type = Enum(
    LevelBahaya,
    name="level_bahaya_enum",
    values_callable=lambda enum_type: [item.value for item in enum_type],
)
road_segment_status_type = Enum(
    RoadSegmentStatus,
    name="road_segment_status_enum",
    values_callable=lambda enum_type: [item.value for item in enum_type],
)
road_report_tipe_type = Enum(
    RoadReportTipe,
    name="road_report_tipe_enum",
    values_callable=lambda enum_type: [item.value for item in enum_type],
)
road_report_status_type = Enum(
    RoadReportStatus,
    name="road_report_status_enum",
    values_callable=lambda enum_type: [item.value for item in enum_type],
)

evacuation_route_segment = Table(
    "evacuation_route_segment",
    Base.metadata,
    Column("route_id", String(50), ForeignKey("evacuation_route.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "segment_id",
        UUID(as_uuid=True),
        ForeignKey("road_segment.segment_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("urutan", Integer, nullable=False),
    CheckConstraint("urutan >= 1", name="ck_evacuation_route_segment_urutan"),
)


class RW(Base):
    __tablename__ = "rw"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nama_rw: Mapped[str] = mapped_column(String(100), nullable=False)
    batas_wilayah = mapped_column(Geometry("POLYGON", srid=4326), nullable=False)
    titik_kumpul = mapped_column(Geometry("POINT", srid=4326), nullable=False)
    data_diperbarui: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    data_kedaluwarsa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    hazards: Mapped[list["Hazard"]] = relationship(back_populates="rw", cascade="all, delete-orphan")
    digital_twin: Mapped["DigitalTwin | None"] = relationship(
        back_populates="rw", cascade="all, delete-orphan", uselist=False
    )
    road_segments: Mapped[list["RoadSegment"]] = relationship(back_populates="rw")
    devices: Mapped[list["PerangkatWarga"]] = relationship(back_populates="rw")

    __table_args__ = (
        Index("idx_rw_batas_wilayah_gist", "batas_wilayah", postgresql_using="gist"),
        Index("idx_rw_titik_kumpul_gist", "titik_kumpul", postgresql_using="gist"),
    )


class Hazard(Base):
    __tablename__ = "hazard"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rw_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rw.id", ondelete="CASCADE"), nullable=False
    )
    sumber: Mapped[str] = mapped_column(String(50), nullable=False)
    jenis: Mapped[str] = mapped_column(String(100), nullable=False)
    level_bahaya: Mapped[LevelBahaya] = mapped_column(
        level_bahaya_type, nullable=False, default=LevelBahaya.AMAN
    )
    tingkat_bahaya: Mapped[float] = mapped_column(Float, nullable=False)
    geometri = mapped_column(Geometry("POLYGON", srid=4326), nullable=False)
    waktu_data: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    terverifikasi: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    rw: Mapped[RW] = relationship(back_populates="hazards")

    __table_args__ = (
        CheckConstraint("tingkat_bahaya >= 0", name="ck_hazard_tingkat_bahaya"),
        Index("idx_hazard_rw_id", "rw_id"),
        Index("idx_hazard_level_bahaya", "level_bahaya"),
        Index("idx_hazard_geometri_gist", "geometri", postgresql_using="gist"),
    )


class DigitalTwin(Base):
    __tablename__ = "digital_twin"
    __table_args__ = (
        CheckConstraint("tinggi_genangan_cm >= 0", name="ck_digital_twin_tinggi_genangan"),
        CheckConstraint("ruas_tertutup >= 0", name="ck_digital_twin_ruas_tertutup"),
        CheckConstraint(
            "estimasi_warga_terdampak >= 0", name="ck_digital_twin_estimasi_warga"
        ),
        CheckConstraint("perangkat_aktif >= 0", name="ck_digital_twin_perangkat_aktif"),
        Index("idx_digital_twin_zona_bahaya_gist", "zona_bahaya", postgresql_using="gist"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rw_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rw.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    zona_bahaya = mapped_column(Geometry("POLYGON", srid=4326), nullable=True)
    tinggi_genangan_cm: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    ruas_tertutup: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimasi_warga_terdampak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    perangkat_aktif: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    diperbarui_pada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    rw: Mapped[RW] = relationship(back_populates="digital_twin")


class RoadSegment(Base):
    __tablename__ = "road_segment"
    __table_args__ = (
        CheckConstraint("panjang_m > 0", name="ck_road_segment_panjang"),
        CheckConstraint("kecepatan_rata_rata_mps > 0", name="ck_road_segment_kecepatan"),
        CheckConstraint("kapasitas_maks > 0", name="ck_road_segment_kapasitas"),
        CheckConstraint("pengguna_aktif >= 0", name="ck_road_segment_pengguna_aktif"),
        Index("idx_road_segment_rw_id", "rw_id"),
        Index("idx_road_segment_status", "status"),
        Index("idx_road_segment_geometri_gist", "geometri", postgresql_using="gist"),
    )

    segment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    rw_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rw.id", ondelete="CASCADE"), nullable=False
    )
    geometri = mapped_column(Geometry("LINESTRING", srid=4326), nullable=False)
    panjang_m: Mapped[float] = mapped_column(Float, nullable=False)
    kecepatan_rata_rata_mps: Mapped[float] = mapped_column(Float, nullable=False, default=1.4)
    kapasitas_maks: Mapped[int] = mapped_column(Integer, nullable=False)
    pengguna_aktif: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[RoadSegmentStatus] = mapped_column(
        road_segment_status_type, nullable=False, default=RoadSegmentStatus.AMAN
    )
    diblokir_manual: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    alasan: Mapped[str] = mapped_column(Text, nullable=False, default="")

    rw: Mapped[RW] = relationship(back_populates="road_segments")
    evacuation_routes: Mapped[list["EvacuationRoute"]] = relationship(
        secondary=evacuation_route_segment, back_populates="segments"
    )


class EvacuationRoute(Base):
    __tablename__ = "evacuation_route"
    __table_args__ = (
        CheckConstraint("jarak_m >= 0", name="ck_evacuation_route_jarak"),
        CheckConstraint("estimasi_menit >= 0", name="ck_evacuation_route_estimasi"),
        CheckConstraint("beban_persen >= 0", name="ck_evacuation_route_beban"),
        Index("idx_evacuation_route_rw_id", "rw_id"),
        Index("idx_evacuation_route_geometri_gist", "geometri", postgresql_using="gist"),
    )

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    rw_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rw.id", ondelete="CASCADE"), nullable=False
    )
    utama: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    jarak_m: Mapped[int] = mapped_column(Integer, nullable=False)
    estimasi_menit: Mapped[int] = mapped_column(Integer, nullable=False)
    beban_persen: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[RoadSegmentStatus] = mapped_column(
        road_segment_status_type, nullable=False, default=RoadSegmentStatus.AMAN
    )
    geometri = mapped_column(Geometry("LINESTRING", srid=4326), nullable=False)
    dihitung_pada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    rw: Mapped[RW] = relationship()
    segments: Mapped[list[RoadSegment]] = relationship(
        secondary=evacuation_route_segment, back_populates="evacuation_routes"
    )


class PerangkatWarga(Base):
    __tablename__ = "perangkat_warga"
    __table_args__ = (
        CheckConstraint("reputasi >= 0.0 AND reputasi <= 1.0", name="ck_perangkat_warga_reputasi"),
        Index("idx_perangkat_warga_rw_id", "rw_id"),
    )

    device_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    rw_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rw.id", ondelete="CASCADE"), nullable=False
    )
    fcm_token: Mapped[str] = mapped_column(Text, nullable=False)
    reputasi: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    terakhir_aktif: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    rw: Mapped[RW] = relationship(back_populates="devices")
    road_reports: Mapped[list["RoadReport"]] = relationship(back_populates="device")


class RoadReport(Base):
    __tablename__ = "road_report"
    __table_args__ = (
        CheckConstraint("lat BETWEEN -90 AND 90", name="ck_road_report_lat"),
        CheckConstraint("lng BETWEEN -180 AND 180", name="ck_road_report_lng"),
        CheckConstraint(
            "skor_kepercayaan >= 0.0 AND skor_kepercayaan <= 1.0",
            name="ck_road_report_skor_kepercayaan",
        ),
        Index("idx_road_report_segment_id", "segment_id"),
        Index("idx_road_report_status", "status"),
        Index("idx_road_report_dibuat_pada", "dibuat_pada"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    segment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("road_segment.segment_id", ondelete="CASCADE"), nullable=False
    )
    device_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("perangkat_warga.device_id", ondelete="CASCADE"), nullable=False
    )
    tipe: Mapped[RoadReportTipe] = mapped_column(road_report_tipe_type, nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    catatan: Mapped[str] = mapped_column(Text, nullable=False, default="")
    skor_kepercayaan: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[RoadReportStatus] = mapped_column(
        road_report_status_type, nullable=False, default=RoadReportStatus.MENUNGGU_TINJAUAN
    )
    dibuat_pada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    diverifikasi_oleh: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    segment: Mapped[RoadSegment] = relationship()
    device: Mapped[PerangkatWarga] = relationship(back_populates="road_reports")
