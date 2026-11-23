<div align="center">

![Dokumen](https://img.shields.io/badge/DOKUMEN-SEQUENCE_DIAGRAM-00f0ff?style=for-the-badge&labelColor=0b1020)
![Versi](https://img.shields.io/badge/VERSI-v1_(rancangan)-7b5cff?style=for-the-badge&labelColor=0b1020)

# 🔄 Sequence Diagram

**HyperEvac System** · Rekayasa Perangkat Lunak · Universitas Samudra

</div>

<img src="../docs/assets/divider.svg" width="100%" alt=""/>

## 1. Agregasi Data, Peringatan Dini & Peta Bahaya (`UC1`, `UC2`, `UC8`)

```mermaid
sequenceDiagram
    autonumber
    actor Warga as Warga Area Rawan
    participant App as Mobile App
    participant API as HyperEvac API
    participant DB as PostGIS DB
    participant Redis as Redis Cache
    participant Agg as DataAggregator
    participant BMKG as Sistem Eksternal BMKG
    participant USGS as Sistem Eksternal USGS
    participant Notif as Notification Service (FCM/APNs)

    Warga->>App: Aktivasi aplikasi
    App->>API: POST /v1/devices/register (device_id, fcm_token, rw_id)
    API->>DB: Simpan PerangkatWarga
    API-->>App: 201 Registered

    loop Polling terjadwal
        Agg->>BMKG: GET data cuaca/gempa
        Agg->>USGS: GET GeoJSON gempa
        loop Retry maksimal 3 kali dengan exponential backoff
            alt Sumber merespons HTTP 200
                BMKG-->>Agg: Payload BMKG
                USGS-->>Agg: Payload USGS
            else Timeout / non-200
                BMKG-->>Agg: Error / timeout
                USGS-->>Agg: Error / timeout
            end
        end
        Agg->>Agg: Validasi & normalisasi WGS 84
        alt Data valid dan tersedia
            Agg->>DB: Upsert Hazard, data_kedaluwarsa = false
            Agg->>Redis: Simpan payload terbaru, data_kedaluwarsa = false
        else Semua retry gagal
            Agg->>Redis: Baca payload terakhir
            Redis-->>Agg: Payload cache + timestamp
            Agg->>Agg: Tandai data_kedaluwarsa = true
            Agg->>DB: Simpan/update Hazard dengan flag kedaluwarsa
        end
        opt level_bahaya >= SIAGA
            Agg->>Notif: Minta kirim peringatan untuk RW terdampak
            Notif-->>App: Push Notification darurat
        end
    end

    Warga->>App: Buka peta bahaya
    App->>API: GET /v1/hazards?rw={id}
    API->>DB: Query RW, Hazard & titik kumpul
    DB-->>API: Data GeoJSON + data_kedaluwarsa
    API-->>App: 200 hazards + atribusi sumber
    App-->>Warga: Tampilkan peta dan status data
```

## 2. Permintaan Rute Evakuasi Dinamis & Anti-Bottleneck (`UC3`)

```mermaid
sequenceDiagram
    autonumber
    actor Warga as Warga Area Rawan
    participant App as Mobile App
    participant API as HyperEvac API
    participant Route as Routing Engine
    participant DB as PostGIS DB
    participant Mapbox as Mapbox API

    Warga->>App: Minta rute evakuasi
    App->>API: GET /v1/routes/evacuation?lat={lat}&lng={lng}
    API->>Route: Hitung rute untuk origin dan RW
    Route->>DB: Ambil RoadSegment dan Hazard aktif
    DB-->>Route: Geometri, status & kapasitas_maks
    Route->>Route: ST_Intersects(RoadSegment.geometri, Hazard.geometri)
    Route->>Route: K-shortest paths, evaluasi pengguna_aktif vs kapasitas_maks
    alt Ditemukan rute aman
        Route->>Mapbox: Minta peta/rute geospasial
        Mapbox-->>Route: Geometri rute utama dan alternatif
        Route->>DB: Simpan pengguna_aktif dan beban_persen
        Route-->>API: Rute aman + beban_persen
        API-->>App: 200 rute utama dan alternatif
        App-->>Warga: Tampilkan navigasi evakuasi
    else Tidak ada rute aman
        Route-->>API: evakuasi_vertikal = true, alert_sar = true
        API-->>App: Instruksi Evakuasi Vertikal + Alert SAR
        App-->>Warga: Tampilkan layar darurat
    end
```

## 3. Laporan SOS, Verifikasi BPBD & Blokir Manual (`UC4`, `UC5`, `UC6`, `UC7`)

```mermaid
sequenceDiagram
    autonumber
    actor Warga as Warga Area Rawan
    actor Operator as Operator BPBD / Tim SAR
    actor Maintainer as Tim Maintainer / DevOps
    participant App as Mobile App
    participant Web as Web Dashboard
    participant API as HyperEvac API
    participant DB as PostGIS DB
    participant Route as Routing Engine

    Warga->>App: Kirim laporan tertutup/aman
    App->>API: POST /v1/reports (device_id, segment_id, tipe, lat, lng)
    API->>DB: Simpan RoadReport & hitung skor_kepercayaan
    alt skor_kepercayaan >= 0.75 dan tipe = tertutup
        API->>DB: Set RoadSegment TERTUTUP_SEMENTARA, laporan terverifikasi_otomatis
        API->>Route: Hitung ulang rute
        API-->>App: 201 status terverifikasi_otomatis
    else skor_kepercayaan < 0.75 atau tipe = aman
        API->>DB: Set laporan menunggu_tinjauan
        API-->>App: 201 status menunggu_tinjauan
    end

    Operator->>Web: Buka antrean laporan
    Web->>API: GET /v1/admin/reports?status=menunggu_tinjauan
    API->>DB: Query RoadReport dan PerangkatWarga
    DB-->>API: Daftar laporan & skor_kepercayaan
    API-->>Web: 200 antrean laporan
    Operator->>Web: Terima atau tolak laporan
    Web->>API: PATCH /v1/admin/reports/{id}
    API->>DB: Perbarui status laporan/reputasi dan status ruas
    API->>Route: Recalculate jika status ruas berubah
    API-->>Web: Status verifikasi terbaru

    Operator->>Web: Blokir ruas manual dengan alasan
    Web->>API: POST /v1/admin/routes/block
    API->>DB: Set TERTUTUP_MANUAL, diblokir_manual = true
    API->>Route: Hitung ulang rute
    API-->>Web: Konfirmasi status ruas
    Operator->>Web: Buka kembali blokir
    Web->>API: DELETE /v1/admin/routes/block/{segment_id}
    API->>DB: Set AMAN, diblokir_manual = false
    API->>Route: Hitung ulang rute
    API-->>Web: Konfirmasi status ruas

    Operator->>Web: Pantau Digital Twin
    Web->>API: GET /v1/twin/{rw_id}
    API->>DB: Ambil snapshot wilayah
    DB-->>API: DigitalTwin
    API-->>Web: tinggi_genangan_cm & estimasi warga terdampak

    Maintainer->>API: GET /v1/health
    API->>DB: Periksa PostGIS dan metrik dependensi
    API-->>Maintainer: Status, usia_cache_detik & latensi_db_ms
```
