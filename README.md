<p align="center">
  <a href="https://git.io/typing-svg">
    <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=800&size=45&pause=1000&color=0D8ABC&center=true&vCenter=true&width=800&height=100&lines=HYPEREVAC+SYSTEM;PERINGATAN+DINI+BENCANA;NAVIGASI+EVAKUASI+LOKAL" alt="HyperEvac System" />
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge&logo=github" alt="Status" />
  <img src="https://img.shields.io/badge/Methodology-Spiral%20Model-blue?style=for-the-badge&logo=opslevel" alt="SDLC" />
  <img src="https://img.shields.io/badge/Course-Rekayasa%20Perangkat%20Lunak-orange?style=for-the-badge&logo=bookstack" alt="RPL" />
  <img src="https://img.shields.io/badge/Platform-Mobile%20%26%20Web-lightgrey?style=for-the-badge" alt="Platform" />
</p>

---

## 📖 Tentang Proyek

**HyperEvac System** adalah sistem informasi peringatan dini dan navigasi evakuasi bencana hyper-lokal untuk memenuhi tugas mata kuliah **Rekayasa Perangkat Lunak**, Program Studi **Informatika, Universitas Samudra**.

Pendekatan **software-only** mengagregasi data publik BMKG dan USGS tanpa sensor fisik. Sistem dirancang dengan **Model Spiral** yang berfokus pada mitigasi risiko *critical-safety*. Digital Twin juga sepenuhnya **software-based, tanpa sensor fisik/IoT**; estimasi tinggi genangan bersumber dari curah hujan BMKG, laporan warga, atau input manual Operator BPBD.

> **Status:** Implementasi Sprint 3 tersedia: backend FastAPI, dashboard operator React, dan aplikasi warga Flutter. Infrastruktur database dan prototipe aggregator Siklus 1 tersimpan di `sprint-3/Setup-Code/`. Validasi lokal mencakup pytest backend, build dashboard, serta analyze dan test mobile; deployment produksi dan integrasi notifikasi FCM/APNs belum diklaim siap.

---

## 📂 Navigasi Berkas & Dokumentasi

### Dokumen Utama & Proposal

- [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md) — Ringkasan teknis untuk konteks pengembangan.
- [Rencana Sprint](./docs/plans/) — Dokumen rencana internal Sprint 3 dan sinkronisasi.
- [Proposal Proyek](./docs/PROPOSAL.md) — Tujuan, kebutuhan, arsitektur, risiko, dan roadmap.
- [Slide Presentasi](./docs/Kelompok%202.pdf) — Materi presentasi kelompok.

### Artefak Sprint 1 (`sprint-1/`)

- [User Story & Acceptance Criteria](./sprint-1/USER-STORY.md)
- [Function Point Analysis](./sprint-1/FUNCTION-POINT.md)
- [Flowchart Algoritma](./sprint-1/FLOWCHART.md)
- [Activity Diagram](./sprint-1/ACTIVITY-DIAGRAM.md)
- [Spesifikasi REST API](./sprint-1/API-SPEC.md)
- [Deployment Architecture](./sprint-1/DEPLOYMENT.md)
- [UI/UX Wireframe](./sprint-1/UI-UX-WIREFRAME.md)

### Artefak Sprint 2 (`sprint-2/`)

- [Context Diagram](./sprint-2/CONTEXT-DIAGRAM.md)
- [Use Case Diagram](./sprint-2/USE-CASE.md)
- [Class Diagram & Model Data Spasial PostGIS (WGS 84 / SRID 4326)](./sprint-2/CLASS-DAN-DATABASE.md)
- [Sequence Diagram](./sprint-2/SEQUENCE-DIAGRAM.md)
- [State Diagram](./sprint-2/STATE-DIAGRAM.md)

### Artefak Sprint 3 (`sprint-3/`, `backend/`, `frontend-dashboard/`, `mobile-app/`)

- [Docker Compose PostgreSQL/PostGIS & Redis](./sprint-3/Setup-Code/docker-compose.yml)
- [Skema Database PostGIS (`schema.sql`)](./sprint-3/Setup-Code/schema.sql)
- [Data Seed Lokal (`seed.sql`)](./sprint-3/Setup-Code/seed.sql)
- [Prototipe Aggregator BMKG Siklus 1](./sprint-3/Setup-Code/aggregator/fetch_bmkg.py)
- [Unit Test Parser](./sprint-3/Setup-Code/aggregator/test_parse.py)
- [Panduan Setup dan Pengujian](./sprint-3/Setup-Code/README.md)
- [Backend API (Python FastAPI)](./backend/)
- [Web Dashboard BPBD (React + Leaflet)](./frontend-dashboard/)
- [Mobile App Warga (Flutter)](./mobile-app/)

---

## ✨ Fitur & Kebutuhan Fungsional

- **FR-01 — Resilient API Aggregation:** Pengambilan data BMKG/USGS secara periodik dengan retry dan Redis fallback cache.
- **FR-02 — Validasi & Normalisasi:** Validasi payload serta normalisasi data geospasial ke WGS 84.
- **FR-03 — Emergency Push Notification:** Peringatan darurat berbasis wilayah melalui FCM/APNs.
- **FR-04 — Dynamic Hazard Mapping:** Peta bahaya RW, poligon risiko, dan titik kumpul aman.
- **FR-05 — Dynamic Evacuation Routing:** Rekomendasi rute yang menghindari ruas berbahaya dan hitung ulang saat status berubah.
- **FR-06 — Trust Score & Offline Queue SOS:** Laporan jalan tertutup/aman, antrean offline, dan penilaian kepercayaan.
- **FR-07 — BPBD Manual Route Control:** Verifikasi laporan serta blokir/buka ruas secara manual.
- **FR-08 — Digital Twin:** Snapshot software-based kondisi RW, genangan estimasi, ruas tertutup, dan warga terdampak; tidak memakai sensor fisik/IoT.
- **FR-09 — Anti-Bottleneck:** Distribusi pengguna ke rute alternatif berdasarkan beban dan kapasitas ruas.
- **FR-10 — Health Monitoring:** Status layanan, usia cache, dan latensi melalui `GET /v1/health`.

---

## 👥 Tim Pengembang

**Mata Kuliah:** Rekayasa Perangkat Lunak · **Program Studi:** Informatika, Universitas Samudra

| Nama & NPM | Peran |
|---|---|
| **Raihan Noor** · `240504148` (Ketua Kelompok) | Project Manager & System Analyst |
| **Muhammad Najwan Jabir A.** · `240504151` | Cloud Backend & API Engineer |
| **Deby Syahdan** · `240504124` | Mobile App Developer |
| **M. Julian Saputra** · `240504092` | Frontend Web Developer |

---

## 🔄 Siklus Pengembangan (Model Spiral)

| Sprint / Siklus | Status | Cakupan |
|---|---|---|
| **Sprint 1 — Siklus Spiral 1** | **Selesai — Analisis/desain dan prototipe terbatas** | Rancangan kebutuhan awal dan aggregator BMKG dengan parsing, retry, cache lokal, dan unit test offline. |
| **Sprint 2 — Siklus Spiral 2** | **Selesai — Pemodelan dan sinkronisasi desain** | Context/use case/class/sequence/state diagrams, kontrak API dan model data target. |
| **Sprint 3 — Siklus Spiral 3** | **Implementasi prototipe — validasi lokal** | Tahap 3A/3B: API, worker, PostGIS/Redis, routing, Digital Twin, dashboard BPBD, aplikasi Flutter dan antrean SOS offline. Load test dan integrasi push produksi masih perlu diverifikasi. |

Estimasi proyek pada [Function Point Analysis](./sprint-1/FUNCTION-POINT.md): **132 UFP**, **158,40 AFP**, sekitar **6.336 LOC**, **950,4 jam-orang**, atau sekitar **13,2 minggu**.

---

## 🛠️ Tech Stack Utama

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Flutter](https://img.shields.io/badge/Flutter-%2302569B.svg?style=for-the-badge&logo=Flutter&logoColor=white)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL%20%2B%20PostGIS-4169e1?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-dc382d?style=for-the-badge&logo=redis&logoColor=white)
![OpenStreetMap](https://img.shields.io/badge/OpenStreetMap-7EBC6F?style=for-the-badge&logo=openstreetmap&logoColor=white)
![Docker](https://img.shields.io/badge/docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

**Implemented:** Backend Python/FastAPI dengan PostgreSQL/PostGIS, Redis, API laporan dan operator, routing serta Digital Twin; dashboard React/TypeScript (Leaflet); aplikasi Flutter dengan peta OpenStreetMap dan antrean SOS offline. Infrastruktur Docker/SQL dan prototipe CLI BMKG tersimpan pada `sprint-3/Setup-Code/`.

**Batasan:** FCM/APNs masih stub, dan load test serta deployment produksi belum diverifikasi. Digital Twin 100% berbasis perangkat lunak; tinggi genangan adalah estimasi BMKG/laporan warga/input operator, bukan pembacaan sensor.

---

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=100&section=footer" alt=""/>
</p>
