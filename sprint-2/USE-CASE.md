<div align="center">

![Dokumen](https://img.shields.io/badge/DOKUMEN-USE_CASE-00f0ff?style=for-the-badge&labelColor=0b1020)
![Versi](https://img.shields.io/badge/VERSI-v1_(rancangan)-7b5cff?style=for-the-badge&labelColor=0b1020)

# 👥 Use Case Diagram

**HyperEvac System** · Rekayasa Perangkat Lunak · Universitas Samudra

</div>

<img src="../assets/divider.svg" width="100%" alt=""/>

## 1. Pemetaan Interaksi Aktor dan Sistem

Diagram berikut memetakan seluruh Kebutuhan Fungsional (**FR-01** hingga **FR-10**) terhadap masing-masing aktor dalam ekosistem HyperEvac.

```mermaid
flowchart LR
    Warga(["📱 Aktor: Warga Area Rawan"])
    Operator(["🖥️ Aktor: BPBD / Tim SAR"])
    Maintainer(["🔧 Aktor: Tim Maintainer"])
    BMKG(["🌩️ Eksternal: BMKG & USGS"])

    subgraph HyperEvac["HyperEvac System"]
        UC1("FR-01, FR-04: Melihat Daftar Bahaya Aktif & Peta RW<br/>(GET /v1/hazards)")
        UC2("FR-03: Menerima Push Notification Darurat Berbasis Lokasi")
        UC3("FR-05, FR-09: Navigasi Rute Evakuasi Utama & Alternatif<br/>(GET /v1/routes/evacuation)")
        UC4("FR-06: Melaporkan Kondisi Jalan Tertutup (Tombol SOS)<br/>(POST /v1/reports)")
        UC5("FR-07: Verifikasi Data & Blokir/Buka Rute Manual<br/>(POST & DELETE /v1/admin/routes/block)")
        UC6("FR-08: Memantau Digital Twin Wilayah & Sebaran Warga<br/>(GET /v1/twin/{rw_id})")
        UC7("FR-10: Memantau Kesehatan Layanan, Trafik & Log<br/>(GET /v1/health)")
        UC8("FR-02: Agregasi, Normalisasi & Validasi Data API Publik")
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

    UC1 -.->|"include"| UC8
    UC5 -.->|"include"| UC3
