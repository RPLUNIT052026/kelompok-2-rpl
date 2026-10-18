---

### 3. File: `docs/Desain-dan-Arsitektur/SEQUENCE-DIAGRAM.md`

```markdown
<div align="center">

![Dokumen](https://img.shields.io/badge/DOKUMEN-SEQUENCE_DIAGRAM-00f0ff?style=for-the-badge&labelColor=0b1020)
![Versi](https://img.shields.io/badge/VERSI-v1_(rancangan)-7b5cff?style=for-the-badge&labelColor=0b1020)

# 🔄 Sequence Diagram

**HyperEvac System** · Rekayasa Perangkat Lunak · Universitas Samudra

</div>

<img src="../assets/divider.svg" width="100%" alt=""/>

## 1. Skenario Penarikan Data Aggregator & Peringatan Dini Warga

Diagram ini menggambarkan alur kerja *Data Aggregator* saat menarik data dari BMKG/USGS, mekanisme *cache fallback* saat API eksternal mengalami gangguan, hingga pengiriman peringatan ke warga.

```mermaid
sequenceDiagram
    autonumber
    actor Warga as Warga Area Rawan
    participant App as Mobile App
    participant API as HyperEvac API (/v1)
    participant DB as PostGIS DB & Cache
    participant Agg as Data Aggregator
    participant BMKG as API BMKG / USGS

    loop Setiap Interval Waktu (Cron)
        Agg->>BMKG: Request Data Cuaca & Gempa Terbaru
        alt API Publik Respons Normal
            BMKG-->>Agg: Payload Data Mentah
            Agg->>Agg: Normalisasi & Validasi Data
            Agg->>DB: Simpan Data (data_kedaluwarsa = false)
        else API Publik Timeout / Down
            BMKG-->>Agg: Connection Error / Timeout
            Agg->>DB: Ambil Cache Terakhir (data_kedaluwarsa = true)
        end
    end

    Warga->>App: Buka Peta Risiko & Bahaya RW
    App->>API: GET /v1/hazards?rw={id}
    API->>DB: Query Data Hazard Aktif RW
    DB-->>API: Dataset Hazard + Flag Status Kedaluwarsa
    API-->>App: 200 OK (JSON Hazards, Atribusi BMKG)
    App-->>Warga: Tampilkan Peta Bahaya & Peringatan Dini
