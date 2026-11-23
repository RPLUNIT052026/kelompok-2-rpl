<div align="center">

![Dokumen](https://img.shields.io/badge/DOKUMEN-CONTEXT_DIAGRAM-00f0ff?style=for-the-badge&labelColor=0b1020)
![Versi](https://img.shields.io/badge/VERSI-v1_(rancangan)-7b5cff?style=for-the-badge&labelColor=0b1020)

# 🌐 Context Diagram

**HyperEvac System** · Rekayasa Perangkat Lunak · Universitas Samudra

</div>

<img src="../docs/assets/divider.svg" width="100%" alt=""/>

## 1. Lingkup dan Lingkungan Sistem

Diagram konteks mendefinisikan batas HyperEvac serta interaksi data dengan aktor dan sistem eksternal.

```mermaid
flowchart LR
    BMKG["🌩️ Sistem Eksternal BMKG<br/>(API Cuaca & Gempa)"]
    USGS["🌍 Sistem Eksternal USGS<br/>(GeoJSON Earthquake Feed)"]
    Mapbox["🗺️ Mapbox API<br/>(Peta & Geospasial)"]
    Push["🔔 Push Notification<br/>(FCM / APNs)"]
    Warga["📱 Warga Area Rawan<br/>(Mobile Flutter)"]
    Operator["🖥️ Operator BPBD / Tim SAR<br/>(Web Dashboard React)"]
    Maintainer["🔧 Tim Maintainer / DevOps<br/>(Cloud Console & Monitoring)"]

    subgraph Scope["Lingkup HyperEvac System (Software-Only)"]
        HyperEvac(("🚨 HyperEvac<br/>API v1, DataAggregator,<br/>Digital Twin & Routing Engine"))
    end

    BMKG -- "Feed cuaca, curah hujan & gempa" --> HyperEvac
    USGS -- "Feed data gempa GeoJSON" --> HyperEvac
    Warga -- "Koordinat, permintaan rute & laporan SOS" --> HyperEvac
    HyperEvac -- "Bahaya, rute evakuasi & status laporan" --> Warga
    Operator -- "Verifikasi Laporan SOS & Blokir/Buka Rute Manual" --> HyperEvac
    HyperEvac -- "Digital Twin, antrean laporan & status ruas" --> Operator
    HyperEvac -- "Permintaan peta/routing" --> Mapbox
    Mapbox -- "Tile, geometri & hasil peta" --> HyperEvac
    HyperEvac -- "Push notification darurat" --> Push
    Push -- "Notifikasi" --> Warga
    Maintainer -- "Permintaan health check dan monitoring" --> HyperEvac
    HyperEvac -- "Status komponen, uptime & usia cache" --> Maintainer
```

## 2. Batas Sistem

- `DataAggregator` adalah komponen internal background scheduler, bukan aktor eksternal.
- Digital Twin sepenuhnya software-based dan tidak bergantung pada sensor fisik/IoT.
- Sprint 1 dan Sprint 2 berisi rancangan dan prototipe terbatas; implementasi layanan target dilakukan pada Sprint 3.
