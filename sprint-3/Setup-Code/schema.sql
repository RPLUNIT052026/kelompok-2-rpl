-- ============================================================================
-- HyperEvac System — PostgreSQL + PostGIS DDL (SRID 4326 / WGS 84)
-- Lokasi kanonik: docs/Setup-Code/schema.sql
-- Acuan: sprint-2/CLASS-DAN-DATABASE.md & sprint-1/API-SPEC.md
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

DO $$ BEGIN
    CREATE TYPE level_bahaya_enum AS ENUM ('AMAN', 'WASPADA', 'SIAGA', 'AWAS');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE road_segment_status_enum AS ENUM (
        'AMAN', 'MENUNGGU_TINJAUAN', 'TERTUTUP_SEMENTARA', 'TERTUTUP', 'TERTUTUP_MANUAL'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE road_report_tipe_enum AS ENUM ('tertutup', 'aman');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE road_report_status_enum AS ENUM (
        'menunggu_tinjauan', 'terverifikasi_otomatis', 'diterima', 'ditolak'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS rw (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nama_rw VARCHAR(100) NOT NULL,
    batas_wilayah GEOMETRY(Polygon, 4326) NOT NULL,
    titik_kumpul GEOMETRY(Point, 4326) NOT NULL,
    data_diperbarui TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    data_kedaluwarsa BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX IF NOT EXISTS idx_rw_batas_wilayah_gist ON rw USING GIST (batas_wilayah);
CREATE INDEX IF NOT EXISTS idx_rw_titik_kumpul_gist ON rw USING GIST (titik_kumpul);

CREATE TABLE IF NOT EXISTS hazard (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rw_id UUID NOT NULL REFERENCES rw(id) ON DELETE CASCADE,
    sumber VARCHAR(50) NOT NULL,
    jenis VARCHAR(100) NOT NULL,
    level_bahaya level_bahaya_enum NOT NULL DEFAULT 'AMAN',
    tingkat_bahaya DOUBLE PRECISION NOT NULL CHECK (tingkat_bahaya >= 0),
    geometri GEOMETRY(Polygon, 4326) NOT NULL,
    waktu_data TIMESTAMPTZ NOT NULL,
    terverifikasi BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX IF NOT EXISTS idx_hazard_rw_id ON hazard (rw_id);
CREATE INDEX IF NOT EXISTS idx_hazard_level_bahaya ON hazard (level_bahaya);
CREATE INDEX IF NOT EXISTS idx_hazard_geometri_gist ON hazard USING GIST (geometri);

-- DigitalTwin is 100% software-based, without physical sensors or IoT.
-- tinggi_genangan_cm is an estimate from BMKG rainfall data, citizen reports,
-- or manual Operator BPBD input.
CREATE TABLE IF NOT EXISTS digital_twin (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rw_id UUID NOT NULL UNIQUE REFERENCES rw(id) ON DELETE CASCADE,
    zona_bahaya GEOMETRY(Polygon, 4326),
    tinggi_genangan_cm DOUBLE PRECISION NOT NULL DEFAULT 0.0 CHECK (tinggi_genangan_cm >= 0),
    ruas_tertutup INTEGER NOT NULL DEFAULT 0 CHECK (ruas_tertutup >= 0),
    estimasi_warga_terdampak INTEGER NOT NULL DEFAULT 0 CHECK (estimasi_warga_terdampak >= 0),
    perangkat_aktif INTEGER NOT NULL DEFAULT 0 CHECK (perangkat_aktif >= 0),
    diperbarui_pada TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_digital_twin_zona_bahaya_gist
    ON digital_twin USING GIST (zona_bahaya);

CREATE TABLE IF NOT EXISTS road_segment (
    segment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rw_id UUID NOT NULL REFERENCES rw(id) ON DELETE CASCADE,
    geometri GEOMETRY(LineString, 4326) NOT NULL,
    panjang_m DOUBLE PRECISION NOT NULL CHECK (panjang_m > 0),
    kecepatan_rata_rata_mps DOUBLE PRECISION NOT NULL DEFAULT 1.4
        CHECK (kecepatan_rata_rata_mps > 0),
    kapasitas_maks INTEGER NOT NULL CHECK (kapasitas_maks > 0),
    pengguna_aktif INTEGER NOT NULL DEFAULT 0 CHECK (pengguna_aktif >= 0),
    status road_segment_status_enum NOT NULL DEFAULT 'AMAN',
    diblokir_manual BOOLEAN NOT NULL DEFAULT FALSE,
    alasan TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_road_segment_rw_id ON road_segment (rw_id);
CREATE INDEX IF NOT EXISTS idx_road_segment_status ON road_segment (status);
CREATE INDEX IF NOT EXISTS idx_road_segment_geometri_gist
    ON road_segment USING GIST (geometri);

CREATE TABLE IF NOT EXISTS evacuation_route (
    id VARCHAR(50) PRIMARY KEY,
    rw_id UUID NOT NULL REFERENCES rw(id) ON DELETE CASCADE,
    utama BOOLEAN NOT NULL DEFAULT FALSE,
    jarak_m INTEGER NOT NULL CHECK (jarak_m >= 0),
    estimasi_menit INTEGER NOT NULL CHECK (estimasi_menit >= 0),
    beban_persen DOUBLE PRECISION NOT NULL DEFAULT 0.0 CHECK (beban_persen >= 0),
    status road_segment_status_enum NOT NULL DEFAULT 'AMAN',
    geometri GEOMETRY(LineString, 4326) NOT NULL,
    dihitung_pada TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_evacuation_route_rw_id ON evacuation_route (rw_id);
CREATE INDEX IF NOT EXISTS idx_evacuation_route_geometri_gist
    ON evacuation_route USING GIST (geometri);

CREATE TABLE IF NOT EXISTS evacuation_route_segment (
    route_id VARCHAR(50) NOT NULL REFERENCES evacuation_route(id) ON DELETE CASCADE,
    segment_id UUID NOT NULL REFERENCES road_segment(segment_id) ON DELETE CASCADE,
    urutan INTEGER NOT NULL CHECK (urutan >= 1),
    PRIMARY KEY (route_id, segment_id)
);

CREATE TABLE IF NOT EXISTS perangkat_warga (
    device_id VARCHAR(128) PRIMARY KEY,
    rw_id UUID NOT NULL REFERENCES rw(id) ON DELETE CASCADE,
    fcm_token TEXT NOT NULL,
    reputasi DOUBLE PRECISION NOT NULL DEFAULT 0.5
        CHECK (reputasi >= 0.0 AND reputasi <= 1.0),
    terakhir_aktif TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_perangkat_warga_rw_id ON perangkat_warga (rw_id);

CREATE TABLE IF NOT EXISTS road_report (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    segment_id UUID NOT NULL REFERENCES road_segment(segment_id) ON DELETE CASCADE,
    device_id VARCHAR(128) NOT NULL REFERENCES perangkat_warga(device_id) ON DELETE CASCADE,
    tipe road_report_tipe_enum NOT NULL,
    lat DOUBLE PRECISION NOT NULL CHECK (lat BETWEEN -90 AND 90),
    lng DOUBLE PRECISION NOT NULL CHECK (lng BETWEEN -180 AND 180),
    catatan TEXT NOT NULL DEFAULT '',
    skor_kepercayaan DOUBLE PRECISION NOT NULL DEFAULT 0.0
        CHECK (skor_kepercayaan >= 0.0 AND skor_kepercayaan <= 1.0),
    status road_report_status_enum NOT NULL DEFAULT 'menunggu_tinjauan',
    dibuat_pada TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    diverifikasi_oleh UUID
);
CREATE INDEX IF NOT EXISTS idx_road_report_segment_id ON road_report (segment_id);
CREATE INDEX IF NOT EXISTS idx_road_report_status ON road_report (status);
CREATE INDEX IF NOT EXISTS idx_road_report_dibuat_pada ON road_report (dibuat_pada DESC);
