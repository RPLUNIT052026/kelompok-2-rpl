<div align="center">

![Dokumen](https://img.shields.io/badge/DOKUMEN-CLASS_DIAGRAM-00f0ff?style=for-the-badge&labelColor=0b1020)
![Versi](https://img.shields.io/badge/VERSI-v1_(rancangan)-7b5cff?style=for-the-badge&labelColor=0b1020)

# 🗂️ Class Diagram & Model Data Spasial PostGIS

**HyperEvac System** · Rekayasa Perangkat Lunak · Universitas Samudra

</div>

<img src="../docs/assets/divider.svg" width="100%" alt=""/>

## 1. Struktur Statis dan Hubungan Antar-Entitas

Model domain untuk data spasial PostGIS dengan koordinat WGS 84 / SRID 4326. `<<Entity>>` mewakili tabel data; `<<Service>>` mewakili logika layanan.

```mermaid
classDiagram
    class RW {
        <<Entity>>
        +UUID id
        +String nama_rw
        +Polygon batas_wilayah
        +Point titik_kumpul
        +DateTime data_diperbarui
        +Boolean data_kedaluwarsa
    }

    class Hazard {
        <<Entity>>
        +UUID id
        +UUID rw_id
        +String sumber
        +String jenis
        +String level_bahaya
        +Float tingkat_bahaya
        +Polygon geometri
        +DateTime waktu_data
        +Boolean terverifikasi
    }

    class DigitalTwin {
        <<Entity>>
        +UUID id
        +UUID rw_id
        +Polygon zona_bahaya
        +Float tinggi_genangan_cm
        +Int ruas_tertutup
        +Int estimasi_warga_terdampak
        +Int perangkat_aktif
        +DateTime diperbarui_pada
    }

    class RoadSegment {
        <<Entity>>
        +UUID segment_id
        +UUID rw_id
        +LineString geometri
        +Float panjang_m
        +Float kecepatan_rata_rata_mps
        +Int kapasitas_maks
        +Int pengguna_aktif
        +String status
        +Boolean diblokir_manual
        +String alasan
    }

    class EvacuationRoute {
        <<Entity>>
        +String id
        +UUID rw_id
        +Boolean utama
        +Int jarak_m
        +Int estimasi_menit
        +Float beban_persen
        +String status
        +LineString geometri
        +DateTime dihitung_pada
    }

    class RoadReport {
        <<Entity>>
        +UUID id
        +UUID segment_id
        +String device_id
        +String tipe
        +Float lat
        +Float lng
        +String catatan
        +Float skor_kepercayaan
        +String status
        +DateTime dibuat_pada
        +UUID diverifikasi_oleh
    }

    class PerangkatWarga {
        <<Entity>>
        +String device_id
        +UUID rw_id
        +String fcm_token
        +Float reputasi
        +DateTime terakhir_aktif
    }

    class DataAggregator {
        <<Service>>
        +fetchBMKG()
        +fetchUSGS()
        +normalizePayload()
        +fallbackToCache()
    }

    class RoutingEngine {
        <<Service>>
        +calculateKShortestPaths()
        +applyAntiBottleneck()
    }

    RW "1" --> "0..*" Hazard : memuat bahaya
    RW "1" --> "1" DigitalTwin : memiliki snapshot
    RW "1" --> "1..*" RoadSegment : mencakup ruas
    RW "1" --> "0..*" PerangkatWarga : menaungi perangkat
    RoadSegment "1..*" --> "1..*" EvacuationRoute : membentuk rute
    RoadSegment "1" --> "0..*" RoadReport : menerima laporan
    PerangkatWarga "1" --> "0..*" RoadReport : mengirim laporan
    DataAggregator "1" --> "0..*" Hazard : menyuplai data
    RoutingEngine ..> RoadSegment : membaca graf
    RoutingEngine ..> Hazard : menghindari bahaya
    RoutingEngine ..> EvacuationRoute : menghasilkan
```

`DigitalTwin` 100% berbasis perangkat lunak (*software-based*, tanpa sensor fisik/IoT). Nilai `tinggi_genangan_cm` adalah estimasi berdasarkan data curah hujan BMKG, laporan warga, atau input manual Operator BPBD, bukan pembacaan sensor.

Implementasi DDL PostgreSQL/PostGIS dengan `SRID 4326` direncanakan pada file terpisah `docs/Setup-Code/schema.sql` di Sprint 3. File Markdown diagram ini bukan file SQL dan tidak boleh di-mount sebagai skrip inisialisasi database.
