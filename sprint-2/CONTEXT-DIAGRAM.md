<div align="center">

![Dokumen](https://img.shields.io/badge/DOKUMEN-CONTEXT_DIAGRAM-00f0ff?style=for-the-badge&labelColor=0b1020)
![Versi](https://img.shields.io/badge/VERSI-v1_(rancangan)-7b5cff?style=for-the-badge&labelColor=0b1020)

# 🌐 Context Diagram

**HyperEvac System** · Rekayasa Perangkat Lunak · Universitas Samudra

</div>

<img src="../assets/divider.svg" width="100%" alt=""/>

## 1. Lingkup dan Lingkungan Sistem

Diagram konteks ini mendefinisikan batasan (*scope*) **HyperEvac System** serta interaksi aliran data dengan seluruh entitas eksternal yang terlibat.

```mermaid
flowchart LR
    BMKG["🌩️ Sistem Eksternal BMKG<br/>(Sumber Data Cuaca & Bahaya)"]
    USGS["🌍 Sistem Eksternal USGS<br/>(Sumber Data Gempa)"]
    Warga["📱 Warga Area Rawan<br/>(Mobile App Client)"]
    Operator["🖥️ BPBD & Tim SAR<br/>(Web Dashboard Operator)"]
    Maintainer["🔧 Tim Maintainer<br/>(Cloud Console Admin)"]

    subgraph Scope["Lingkup HyperEvac System (Software-Only)"]
        HyperEvac(("🚨 HyperEvac<br/>System<br/>(API v1 & Aggregator)"))
    end

    BMKG -- "Feed Data Cuaca & Iklim" --> HyperEvac
    USGS -- "Feed Data Gempa Bumi" --> HyperEvac
    Warga -- "Koordinat GPS, Permintaan Rute &<br/>Laporan Crowdsourcing (Tombol SOS)" --> HyperEvac
    HyperEvac -- "Push Notification Peringatan Dini &<br/>Rute Evakuasi Interaktif (Mapbox)" --> Warga
    Operator -- "Verifikasi Data Bahaya &<br/>Blokir/Buka Rute Manual" --> HyperEvac
    HyperEvac -- "Visualisasi Digital Twin Wilayah &<br/>Sebaran Warga Real-Time" --> Operator
    Maintainer -- "Monitoring Uptime, Log Trafik &<br/>Health Check (/v1/health)" --> HyperEvac
    HyperEvac -- "Status Komponen Cloud & Load Balancer" --> Maintainer

