<div align="center">

![Dokumen](https://img.shields.io/badge/DOKUMEN-USE_CASE-00f0ff?style=for-the-badge&labelColor=0b1020)
![Versi](https://img.shields.io/badge/VERSI-v1_(rancangan)-7b5cff?style=for-the-badge&labelColor=0b1020)

# 👥 Use Case Diagram

**HyperEvac System** · Rekayasa Perangkat Lunak · Universitas Samudra

</div>

<img src="../docs/assets/divider.svg" width="100%" alt=""/>

## 1. Pemetaan Interaksi Aktor dan Sistem

Diagram memetakan FR-01 sampai FR-10 kepada aktor, use case, dan kontrak endpoint yang dirancang.

```mermaid
flowchart LR
    Warga(["📱 Aktor: Warga Area Rawan"])
    Operator(["🖥️ Aktor: Operator BPBD / Tim SAR"])
    Maintainer(["🔧 Aktor: Tim Maintainer / DevOps"])
    BMKG(["🌩️ Eksternal: Sistem Eksternal BMKG"])
    USGS(["🌍 Eksternal: Sistem Eksternal USGS"])

    subgraph HyperEvac["HyperEvac System"]
        UC1("UC1 — FR-04: Melihat Daftar Bahaya Aktif & Peta RW<br/>GET /v1/hazards?rw={id}")
        UC2("UC2 — FR-03: Push Notification Darurat<br/>POST /v1/devices/register")
        UC3("UC3 — FR-05, FR-09: Navigasi Rute Utama/Alternatif & Anti-Bottleneck<br/>GET /v1/routes/evacuation")
        UC4("UC4 — FR-06: Laporan Jalan Tertutup/Aman (SOS)<br/>POST /v1/reports")
        UC5("UC5 — FR-07: Antrean, Verifikasi & Blokir/Buka Rute<br/>GET /v1/admin/reports; PATCH /v1/admin/reports/{id}; POST /v1/admin/routes/block; DELETE /v1/admin/routes/block/{segment_id}")
        UC6("UC6 — FR-08: Digital Twin Wilayah<br/>GET /v1/twin/{rw_id}")
        UC7("UC7 — FR-10: Health Check & Monitoring<br/>GET /v1/health")
        UC8("UC8 — FR-01, FR-02: Agregasi, Validasi, Normalisasi & Cache Fallback BMKG/USGS")
    end

    Warga --> UC1
    Warga --> UC2
    Warga --> UC3
    Warga --> UC4
    Operator --> UC1
    Operator --> UC5
    Operator --> UC6
    Maintainer --> UC7
    BMKG --> UC8
    USGS --> UC8
    UC2 -.->|"include"| UC8
    UC4 -.->|"extend"| UC3
```

## 2. Pemetaan FR, Use Case, User Story & Endpoint

| FR | Use Case | User Story | Endpoint / Mekanisme |
|---|---|---|---|
| FR-01 | UC8 | US-01 | Worker DataAggregator: fetch BMKG/USGS, retry, Redis fallback |
| FR-02 | UC8 | US-02 | Validasi dan normalisasi geospasial WGS 84 |
| FR-03 | UC2 | US-03 | `POST /v1/devices/register` dan Notification Service |
| FR-04 | UC1 | US-04 | `GET /v1/hazards?rw={id}` |
| FR-05 | UC3 | US-05 | `GET /v1/routes/evacuation?lat={lat}&lng={lng}` |
| FR-06 | UC4 | US-07 | `POST /v1/reports` |
| FR-07 | UC5 | US-08 | `GET /v1/admin/reports`; `PATCH /v1/admin/reports/{id}`; `POST /v1/admin/routes/block`; `DELETE /v1/admin/routes/block/{segment_id}` |
| FR-08 | UC6 | US-09 | `GET /v1/twin/{rw_id}` |
| FR-09 | UC3 | US-06 | Distribusi rute alternatif saat beban ruas > 80% |
| FR-10 | UC7 | US-10 | `GET /v1/health` |
