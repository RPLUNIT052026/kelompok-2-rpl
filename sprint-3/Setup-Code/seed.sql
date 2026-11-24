-- ============================================================================
-- HyperEvac System — Seed Data Demo Kota Langsa, Aceh (SRID 4326 / WGS 84)
-- Nama lokasi mengikuti wilayah/landmark lokal; batas RW dan ruas adalah
-- geometri ilustratif untuk demo, bukan batas kadaster atau survei jalan resmi.
-- Koordinat landmark: OpenStreetMap contributors (ODbL).
-- ============================================================================

INSERT INTO rw (id, nama_rw, batas_wilayah, titik_kumpul, data_diperbarui, data_kedaluwarsa)
VALUES
    (
        '3f0c6b1e-0000-0000-0000-000000000001',
        'RW 05 — Gampong Jawa, Langsa Kota',
        ST_GeomFromText(
            'POLYGON((97.958 4.462, 97.970 4.462, 97.970 4.476, 97.958 4.476, 97.958 4.462))',
            4326
        ),
        -- Lapangan Merdeka Langsa: 4.4708906, 97.9664134
        ST_GeomFromText('POINT(97.9664134 4.4708906)', 4326), NOW(), FALSE
    ),
    (
        '3f0c6b1e-0000-0000-0000-000000000002',
        'RW 06 — Peukan Langsa, Langsa Kota',
        ST_GeomFromText(
            'POLYGON((97.970 4.462, 97.985 4.462, 97.985 4.476, 97.970 4.476, 97.970 4.462))',
            4326
        ),
        -- Masjid Raya Kota Langsa: 4.4697705, 97.9712979
        ST_GeomFromText('POINT(97.9712979 4.4697705)', 4326), NOW(), FALSE
    ),
    (
        '3f0c6b1e-0000-0000-0000-000000000003',
        'RW 07 — Meurandeh Dayah, Langsa Lama',
        ST_GeomFromText(
            'POLYGON((97.965 4.450, 97.980 4.450, 97.980 4.462, 97.965 4.462, 97.965 4.450))',
            4326
        ),
        -- Universitas Samudra: 4.4560053, 97.9721465
        ST_GeomFromText('POINT(97.9721465 4.4560053)', 4326), NOW(), FALSE
    )
ON CONFLICT (id) DO UPDATE SET
    nama_rw = EXCLUDED.nama_rw,
    batas_wilayah = EXCLUDED.batas_wilayah,
    titik_kumpul = EXCLUDED.titik_kumpul,
    data_diperbarui = EXCLUDED.data_diperbarui,
    data_kedaluwarsa = EXCLUDED.data_kedaluwarsa;

INSERT INTO road_segment (
    segment_id, rw_id, geometri, panjang_m, kecepatan_rata_rata_mps,
    kapasitas_maks, pengguna_aktif, status, diblokir_manual, alasan
)
VALUES
    -- RW 05: tiga jalur tersambung dari pusat peta ke Lapangan Merdeka.
    ('b7a6c5d4-0000-0000-0000-000000000030', '3f0c6b1e-0000-0000-0000-000000000001',
     ST_GeomFromText('LINESTRING(97.9683 4.4683, 97.9672 4.4688)', 4326),
     145.0, 1.4, 400, 100, 'AMAN', FALSE, 'Jl. Gampong Jawa — jalur utama'),
    ('b7a6c5d4-0000-0000-0000-000000000031', '3f0c6b1e-0000-0000-0000-000000000001',
     ST_GeomFromText('LINESTRING(97.9672 4.4688, 97.9668 4.4698)', 4326),
     120.0, 1.4, 400, 80, 'AMAN', FALSE, 'Jl. Gampong Jawa — zona simulasi WASPADA'),
    ('b7a6c5d4-0000-0000-0000-000000000032', '3f0c6b1e-0000-0000-0000-000000000001',
     ST_GeomFromText('LINESTRING(97.9683 4.4683, 97.9692 4.4675)', 4326),
     135.0, 1.4, 400, 200, 'AMAN', FALSE, 'Jalur B — alternatif menuju pusat kota'),
    ('b7a6c5d4-0000-0000-0000-000000000033', '3f0c6b1e-0000-0000-0000-000000000001',
     ST_GeomFromText('LINESTRING(97.9692 4.4675, 97.9700 4.4685)', 4326),
     155.0, 1.4, 400, 180, 'AMAN', FALSE, 'Jalur B — koridor Peukan Langsa'),
    ('b7a6c5d4-0000-0000-0000-000000000034', '3f0c6b1e-0000-0000-0000-000000000001',
     ST_GeomFromText('LINESTRING(97.9700 4.4685, 97.9688 4.4700, 97.9664134 4.4708906)', 4326),
     390.0, 1.4, 500, 100, 'AMAN', FALSE, 'Koridor menuju Lapangan Merdeka'),
    ('b7a6c5d4-0000-0000-0000-000000000035', '3f0c6b1e-0000-0000-0000-000000000001',
     ST_GeomFromText('LINESTRING(97.9683 4.4683, 97.9690 4.4715)', 4326),
     365.0, 1.4, 500, 90, 'AMAN', FALSE, 'Jalur C — alternatif sisi timur'),
    ('b7a6c5d4-0000-0000-0000-000000000036', '3f0c6b1e-0000-0000-0000-000000000001',
     ST_GeomFromText('LINESTRING(97.9690 4.4715, 97.9664134 4.4708906)', 4326),
     310.0, 1.4, 500, 75, 'AMAN', FALSE, 'Jalur C — sambungan Lapangan Merdeka'),
    -- RW 06: ruas bertemu pada node bersama menuju Masjid Raya Kota Langsa.
    ('b7a6c5d4-0000-0000-0000-000000000040', '3f0c6b1e-0000-0000-0000-000000000002',
     ST_GeomFromText('LINESTRING(97.9760 4.4690, 97.9748 4.4696)', 4326),
     150.0, 1.4, 400, 90, 'AMAN', FALSE, 'Jl. Peukan Langsa — jalur utama'),
    ('b7a6c5d4-0000-0000-0000-000000000041', '3f0c6b1e-0000-0000-0000-000000000002',
     ST_GeomFromText('LINESTRING(97.9748 4.4696, 97.9734 4.4700)', 4326),
     160.0, 1.4, 400, 80, 'AMAN', FALSE, 'Jl. Peukan Langsa — zona simulasi SIAGA'),
    ('b7a6c5d4-0000-0000-0000-000000000042', '3f0c6b1e-0000-0000-0000-000000000002',
     ST_GeomFromText('LINESTRING(97.9734 4.4700, 97.9712979 4.4697705)', 4326),
     240.0, 1.4, 400, 120, 'AMAN', FALSE, 'Akses Masjid Raya Kota Langsa'),
    ('b7a6c5d4-0000-0000-0000-000000000043', '3f0c6b1e-0000-0000-0000-000000000002',
     ST_GeomFromText('LINESTRING(97.9760 4.4690, 97.9772 4.4670)', 4326),
     265.0, 1.4, 500, 100, 'AMAN', FALSE, 'Jalur alternatif sisi timur'),
    ('b7a6c5d4-0000-0000-0000-000000000044', '3f0c6b1e-0000-0000-0000-000000000002',
     ST_GeomFromText('LINESTRING(97.9772 4.4670, 97.9740 4.4665)', 4326),
     360.0, 1.4, 500, 90, 'AMAN', FALSE, 'Koridor alternatif Peukan Langsa'),
    ('b7a6c5d4-0000-0000-0000-000000000045', '3f0c6b1e-0000-0000-0000-000000000002',
     ST_GeomFromText('LINESTRING(97.9740 4.4665, 97.9712979 4.4697705)', 4326),
     470.0, 1.4, 500, 75, 'AMAN', FALSE, 'Sambungan alternatif Masjid Raya'),
    -- RW 07: jaringan Meurandeh Dayah dengan titik kumpul area Universitas Samudra.
    ('b7a6c5d4-0000-0000-0000-000000000050', '3f0c6b1e-0000-0000-0000-000000000003',
     ST_GeomFromText('LINESTRING(97.9710 4.4570, 97.9690 4.4575)', 4326),
     230.0, 1.4, 400, 70, 'AMAN', FALSE, 'Jl. Meurandeh Dayah — jalur utama'),
    ('b7a6c5d4-0000-0000-0000-000000000051', '3f0c6b1e-0000-0000-0000-000000000003',
     ST_GeomFromText('LINESTRING(97.9690 4.4575, 97.9721465 4.4560053)', 4326),
     390.0, 1.4, 400, 50, 'AMAN', FALSE, 'Akses Universitas Samudra'),
    ('b7a6c5d4-0000-0000-0000-000000000052', '3f0c6b1e-0000-0000-0000-000000000003',
     ST_GeomFromText('LINESTRING(97.9710 4.4570, 97.9725 4.4590)', 4326),
     280.0, 1.4, 500, 100, 'AMAN', FALSE, 'Jalur alternatif Meurandeh'),
    ('b7a6c5d4-0000-0000-0000-000000000053', '3f0c6b1e-0000-0000-0000-000000000003',
     ST_GeomFromText('LINESTRING(97.9725 4.4590, 97.9750 4.4580)', 4326),
     300.0, 1.4, 500, 95, 'AMAN', FALSE, 'Koridor alternatif kampus'),
    ('b7a6c5d4-0000-0000-0000-000000000054', '3f0c6b1e-0000-0000-0000-000000000003',
     ST_GeomFromText('LINESTRING(97.9750 4.4580, 97.9721465 4.4560053)', 4326),
     370.0, 1.4, 500, 80, 'AMAN', FALSE, 'Sambungan alternatif kampus'),
    ('b7a6c5d4-0000-0000-0000-000000000055', '3f0c6b1e-0000-0000-0000-000000000003',
     ST_GeomFromText('LINESTRING(97.9710 4.4570, 97.9700 4.4540, 97.9721465 4.4560053)', 4326),
     430.0, 1.4, 500, 65, 'AMAN', FALSE, 'Jalur alternatif sisi selatan')
ON CONFLICT (segment_id) DO UPDATE SET
    rw_id = EXCLUDED.rw_id,
    geometri = EXCLUDED.geometri,
    panjang_m = EXCLUDED.panjang_m,
    kecepatan_rata_rata_mps = EXCLUDED.kecepatan_rata_rata_mps,
    kapasitas_maks = EXCLUDED.kapasitas_maks,
    pengguna_aktif = EXCLUDED.pengguna_aktif,
    status = EXCLUDED.status,
    diblokir_manual = EXCLUDED.diblokir_manual,
    alasan = EXCLUDED.alasan;

INSERT INTO hazard (
    id, rw_id, sumber, jenis, level_bahaya, tingkat_bahaya, geometri, waktu_data, terverifikasi
)
VALUES
    (
        'a1b2c3d4-0000-0000-0000-000000000010',
        '3f0c6b1e-0000-0000-0000-000000000001',
        'BMKG', 'cuaca_ekstrem', 'SIAGA', 3.2,
        ST_GeomFromText(
            'POLYGON((97.9666 4.4693, 97.9671 4.4693, 97.9671 4.4696, 97.9666 4.4696, 97.9666 4.4693))',
            4326
        ),
        NOW(), FALSE
    ),
    (
        'a1b2c3d4-0000-0000-0000-000000000011',
        '3f0c6b1e-0000-0000-0000-000000000002',
        'BMKG', 'hujan_lebat', 'SIAGA', 3.5,
        ST_GeomFromText(
            'POLYGON((97.9732 4.4697, 97.9737 4.4697, 97.9737 4.4702, 97.9732 4.4702, 97.9732 4.4697))',
            4326
        ),
        NOW(), FALSE
    ),
    (
        'a1b2c3d4-0000-0000-0000-000000000012',
        '3f0c6b1e-0000-0000-0000-000000000003',
        'BMKG', 'cuaca_ekstrem', 'WASPADA', 2.0,
        ST_GeomFromText(
            'POLYGON((97.9688 4.4573, 97.9695 4.4573, 97.9695 4.4578, 97.9688 4.4578, 97.9688 4.4573))',
            4326
        ),
        NOW(), FALSE
    )
ON CONFLICT (id) DO UPDATE SET
    rw_id = EXCLUDED.rw_id,
    sumber = EXCLUDED.sumber,
    jenis = EXCLUDED.jenis,
    level_bahaya = EXCLUDED.level_bahaya,
    tingkat_bahaya = EXCLUDED.tingkat_bahaya,
    geometri = EXCLUDED.geometri,
    waktu_data = EXCLUDED.waktu_data,
    terverifikasi = EXCLUDED.terverifikasi;

-- Digital Twin is software-based; genangan adalah estimasi BMKG/laporan warga,
-- bukan data sensor. Poligon snapshot mengikuti zona pada tiap wilayah.
INSERT INTO digital_twin (
    id, rw_id, zona_bahaya, tinggi_genangan_cm, ruas_tertutup,
    estimasi_warga_terdampak, perangkat_aktif, diperbarui_pada
)
VALUES
    ('5b2a1c00-0000-0000-0000-000000000001',
     '3f0c6b1e-0000-0000-0000-000000000001',
     ST_GeomFromText(
         'POLYGON((97.9666 4.4693, 97.9671 4.4693, 97.9671 4.4696, 97.9666 4.4696, 97.9666 4.4693))',
         4326
     ),
     18.0, 0, 1420, 12, NOW()),
    ('5b2a1c00-0000-0000-0000-000000000002',
     '3f0c6b1e-0000-0000-0000-000000000002',
     ST_GeomFromText(
         'POLYGON((97.9732 4.4697, 97.9737 4.4697, 97.9737 4.4702, 97.9732 4.4702, 97.9732 4.4697))',
         4326
     ),
     35.0, 0, 980, 8, NOW()),
    ('5b2a1c00-0000-0000-0000-000000000003',
     '3f0c6b1e-0000-0000-0000-000000000003',
     ST_GeomFromText(
         'POLYGON((97.9688 4.4573, 97.9695 4.4573, 97.9695 4.4578, 97.9688 4.4578, 97.9688 4.4573))',
         4326
     ),
     12.0, 0, 640, 5, NOW())
ON CONFLICT (rw_id) DO UPDATE SET
    zona_bahaya = EXCLUDED.zona_bahaya,
    tinggi_genangan_cm = EXCLUDED.tinggi_genangan_cm,
    ruas_tertutup = EXCLUDED.ruas_tertutup,
    estimasi_warga_terdampak = EXCLUDED.estimasi_warga_terdampak,
    perangkat_aktif = EXCLUDED.perangkat_aktif,
    diperbarui_pada = EXCLUDED.diperbarui_pada;

INSERT INTO perangkat_warga (device_id, rw_id, fcm_token, reputasi, terakhir_aktif)
VALUES (
    'device-01',
    '3f0c6b1e-0000-0000-0000-000000000001',
    'seed-fcm-token-placeholder', 0.5, NOW()
)
ON CONFLICT (device_id) DO UPDATE SET
    rw_id = EXCLUDED.rw_id,
    fcm_token = EXCLUDED.fcm_token,
    terakhir_aktif = EXCLUDED.terakhir_aktif;

INSERT INTO road_report (
    id, segment_id, device_id, tipe, lat, lng, catatan,
    skor_kepercayaan, status, dibuat_pada
)
VALUES (
    'c9d8e7f6-0000-0000-0000-000000000020',
    'b7a6c5d4-0000-0000-0000-000000000032',
    'device-01',
    'tertutup',
    4.4675,
    97.9692,
    'Laporan simulasi genangan pada jalur alternatif RW 05, Gampong Jawa.',
    0.68,
    'menunggu_tinjauan',
    NOW()
)
ON CONFLICT (id) DO UPDATE SET
    segment_id = EXCLUDED.segment_id,
    device_id = EXCLUDED.device_id,
    tipe = EXCLUDED.tipe,
    lat = EXCLUDED.lat,
    lng = EXCLUDED.lng,
    catatan = EXCLUDED.catatan,
    skor_kepercayaan = EXCLUDED.skor_kepercayaan,
    status = EXCLUDED.status,
    dibuat_pada = EXCLUDED.dibuat_pada;
