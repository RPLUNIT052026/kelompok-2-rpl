<div align="center">

![Dokumen](https://img.shields.io/badge/DOKUMEN-CLASS_DIAGRAM-00f0ff?style=for-the-badge&labelColor=0b1020)
![Versi](https://img.shields.io/badge/VERSI-v1_(rancangan)-7b5cff?style=for-the-badge&labelColor=0b1020)

# 🗂️ Class Diagram & Model Data

**HyperEvac System** · Rekayasa Perangkat Lunak · Universitas Samudra

</div>

<img src="../assets/divider.svg" width="100%" alt=""/>

## 1. Struktur Statis dan Hubungan Antar-Entitas

Diagram kelas ini memodelkan struktur basis data spasial (PostGIS) dan objek layanan yang mendukung arsitektur *microservices* HyperEvac.

```mermaid
classDiagram
    class RW {
        +UUID id
        +String nama_rw
        +DateTime data_diperbarui
        +Boolean data_kedaluwarsa
        +getActiveHazards() List~Hazard~
        +getDigitalTwinSnapshot() DigitalTwin
    }

    class Hazard {
        +UUID id
        +UUID rw_id
        +String sumber
        +String jenis
        +Float tingkat_bahaya
        +DateTime waktu_data
        +Boolean terverifikasi
    }

    class DigitalTwin {
        +UUID rw_id
        +Polygon zona_bahaya
        +Int ruas_tertutup
        +Int perangkat_aktif
        +Int latensi_ms
    }

    class RoadSegment {
        +UUID segment_id
        +String status
        +Boolean diblokir_manual
        +String alasan
        +blockSegment(String alasan)
        +unblockSegment()
    }

    class EvacuationRoute {
        +String id
        +Boolean utama
        +Int jarak_m
        +Int estimasi_menit
        +String status
        +LineString geometri
        +recalculate()
    }

    class RoadReport {
        +UUID id
        +String tipe
        +Float lat
        +Float lng
        +String catatan
        +Float skor_kepercayaan
        +String status
    }

    class DataAggregator {
        +String source_url
        +int timeout_ms
        +fetchBMKG()
        +validatePayload()
    }

    RW "1" --> "0..*" Hazard : memuat bahaya
    RW "1" --> "1" DigitalTwin : direpresentasikan
    RW "1" --> "1..*" RoadSegment : mencakup wilayah jalan
    RoadSegment "1..*" --> "1..*" EvacuationRoute : membentuk jalur
    RoadReport "0..*" --> "1" RoadSegment : melaporkan kondisi
    DataAggregator "1" --> "0..*" Hazard : menyuplai data periodik