# PROJECT_OVERVIEW.md

## 1. Ringkasan Proyek & Tujuan Utama

**HyperEvac System** adalah prototipe full-stack peringatan dini dan navigasi evakuasi hyper-lokal untuk warga dan Operator BPBD/Tim SAR. Cakupan meliputi agregasi BMKG/USGS, peta bahaya, routing evakuasi, laporan SOS, kendali ruas manual, dan dashboard Digital Twin.

Repository mencakup dokumentasi Sprint 1–2, backend Sprint 3A/3B, dashboard web, aplikasi warga Flutter, serta prototipe CLI BMKG Siklus 1. Digital Twin 100% berbasis perangkat lunak, tanpa sensor fisik/IoT; `tinggi_genangan_cm` merupakan estimasi dari BMKG, laporan warga, atau input manual Operator BPBD.

## 2. Tech Stack & Dependensi Utama

| Teknologi | Versi / Spesifikasi | Fungsi |
|---|---|---|
| Python backend | Python `3.11` (Docker); FastAPI `>= 0.115`, Pydantic `>= 2.9` | REST API, validasi skema, service dan worker |
| SQLAlchemy / GeoAlchemy2 | `>= 2.0.35` / `>= 0.15.2` | ORM dan geometri PostgreSQL/PostGIS |
| psycopg / Redis | psycopg v3 `>= 3.2`; Redis client `>= 5.1` | Koneksi basis data dan cache/fallback |
| PostgreSQL/PostGIS | `postgis/postgis:16-3.4-alpine` | Penyimpanan data dan geometri |
| Redis | `redis:7-alpine` | Cache/snapshot dan dukungan antrean |
| React / Vite / TypeScript | `18.3.1` / `8.3.6` / `~7.0.2` | Dashboard operator |
| TanStack Query / Axios | `5.62.7` / `1.7.9` | Cache state server dan HTTP |
| Leaflet / React-Leaflet / Tailwind | `1.9.4` / `4.2.1` / `3.4.17` | Peta dan styling dashboard |
| Flutter / Dart | Flutter `>= 3.35`; Dart `^3.9` | Aplikasi warga |
| Riverpod / Dio / Hive | `2.6.1` / `5.7` / `1.1.0` | State, HTTP, antrean offline mobile |
| flutter_map / connectivity_plus / geolocator | `7.0.2` / `6.1.4` / `13.0.2` | Peta OSM, status jaringan, lokasi perangkat |
| `docs/Setup-Code/aggregator/` | Python `requests` CLI prototype | Referensi Sprint 1 untuk fetch BMKG, parser, retry dan file-cache |

## 3. Struktur Folder & Penjelasan Direktori

```text
/
├── README.md                         Ikhtisar proyek dan navigasi dokumen
├── PROJECT_OVERVIEW.md               Konteks teknis repository untuk AI/developer
├── .gitignore                        Aturan ignore lintas proyek
├── backend/                          FastAPI, service, worker, skema dan tes Sprint 3
├── frontend-dashboard/               Dashboard React/Vite/TypeScript BPBD
├── mobile-app/                       Aplikasi Flutter warga (Android/iOS)
├── sprint-1/                         User story, FP, flow/activity, API, deployment, UI/UX
├── sprint-2/                         Context/use case/class/data/sequence/state diagrams
└── docs/
    ├── plans/                        Rencana internal sinkronisasi dan Sprint 3
    ├── PROPOSAL.md                   Proposal akademik dan kebutuhan
    ├── Kelompok 2.pdf                Materi presentasi
    ├── assets/                       SVG banner dan divider
    ├── Desain-dan-Arsitektur/        README rujukan ke artefak Sprint 1–2
    └── Setup-Code/                   Compose, DDL, seed dan prototipe aggregator
```

Dokumen perencanaan internal disimpan di `docs/plans/`. Sumber desain kanonik berada di `sprint-1/` dan `sprint-2/`; prototipe `docs/Setup-Code/aggregator/fetch_bmkg.py` tetap dipisahkan dari service aggregator backend.

## 4. Arsitektur & Alur Data

### Implementasi prototipe

`docs/Setup-Code/aggregator/fetch_bmkg.py` mengambil API gempa dan prakiraan cuaca BMKG, melakukan retry eksponensial hingga tiga percobaan, menyimpan payload ke file JSON lokal, dan memakai cache terakhir jika seluruh request gagal. Payload diparse menjadi dataclass, dinilai dengan heuristik `AMAN`/`WASPADA`/`SIAGA`, lalu dicetak sebagai tabel atau JSON. Tidak ada API server, scheduler berulang, penyimpanan database, atau Redis pada prototipe.

### Arsitektur Sprint 3

- Dashboard React dan aplikasi Flutter memakai REST API `/v1`; konfigurasi API dapat dioverride per lingkungan.
- `DataAggregator` berkala mengambil BMKG/USGS, memvalidasi data dan memakai cache Redis saat sumber gagal.
- FastAPI/service menyimpan data spasial di PostgreSQL/PostGIS (WGS 84, SRID 4326); skema dan seed ada di `docs/Setup-Code/`.
- `RoutingEngine` menghindari hazard dengan `ST_Intersects`, memilih rute dan menghitung beban terhadap kapasitas segmen.
- Laporan warga diproses dengan trust score; operator dapat memverifikasi laporan dan memblokir/membuka ruas secara manual.
- Jika tak ada rute aman, API mengembalikan instruksi evakuasi vertikal dan status Alert SAR.
- `DigitalTwinService` menghitung estimasi dari BMKG, laporan warga dan input operator—tanpa sensor fisik/IoT.
- Push FCM/APNs masih stub; implementasi notifikasi produksi belum tersedia.

### Endpoint API yang diimplementasikan

1. `GET /v1/hazards?rw={id}`
2. `GET /v1/routes/evacuation?lat={lat}&lng={lng}`
3. `POST /v1/reports`
4. `POST /v1/devices/register`
5. `GET /v1/admin/reports?status=menunggu_tinjauan`
6. `PATCH /v1/admin/reports/{id}`
7. `POST /v1/admin/routes/block`
8. `DELETE /v1/admin/routes/block/{segment_id}`
9. `GET /v1/twin/{rw_id}`
10. `GET /v1/health`
11. `GET /v1/admin/routes/segments?rw={rw_id}`

Status `RoadSegment`: `AMAN`, `MENUNGGU_TINJAUAN`, `TERTUTUP_SEMENTARA`, `TERTUTUP`, `TERTUTUP_MANUAL`. Status `RoadReport`: `menunggu_tinjauan`, `terverifikasi_otomatis`, `diterima`, `ditolak`. Flag cache: `data_kedaluwarsa`.

## 5. File Kunci

| File | Fungsi |
|---|---|
| [README.md](./README.md) | Navigasi, fitur, tim, stack, roadmap |
| [backend/app/main.py](./backend/app/main.py) | FastAPI app, CORS dan lifecycle scheduler |
| [backend/app/api/v1/router.py](./backend/app/api/v1/router.py) | Registrasi router `/v1` |
| [backend/app/models/entities.py](./backend/app/models/entities.py) | Entitas SQLAlchemy dan model spasial |
| [backend/app/services/routing_engine.py](./backend/app/services/routing_engine.py) | Perhitungan rute evakuasi dan fallback vertikal |
| [backend/app/services/aggregator.py](./backend/app/services/aggregator.py) | Fetch BMKG/USGS, validasi, persistence dan cache |
| [backend/app/services/report_service.py](./backend/app/services/report_service.py) | Laporan, verifikasi operator dan safety rule ruas |
| [backend/app/services/digital_twin_service.py](./backend/app/services/digital_twin_service.py) | Snapshot Digital Twin software-based |
| [sprint-1/API-SPEC.md](./sprint-1/API-SPEC.md) | Kontrak dan contoh payload endpoint |
| [sprint-1/FUNCTION-POINT.md](./sprint-1/FUNCTION-POINT.md) | Perhitungan FP dan effort |
| [sprint-1/FLOWCHART.md](./sprint-1/FLOWCHART.md) | Aggregator, routing, dan Trust Score |
| [sprint-2/CLASS-DAN-DATABASE.md](./sprint-2/CLASS-DAN-DATABASE.md) | Tujuh entitas domain dan layanan |
| [sprint-2/USE-CASE.md](./sprint-2/USE-CASE.md) | Pemetaan aktor, FR, UC, US, dan endpoint |
| [frontend-dashboard/src/pages/DashboardPage.tsx](./frontend-dashboard/src/pages/DashboardPage.tsx) | Alur utama dashboard operator |
| [mobile-app/lib/main.dart](./mobile-app/lib/main.dart) | Entry point, Hive dan ProviderScope aplikasi warga |
| [mobile-app/lib/data/services/offline_queue_service.dart](./mobile-app/lib/data/services/offline_queue_service.dart) | Persistensi dan auto-sync antrean laporan SOS |
| [docs/Setup-Code/schema.sql](./docs/Setup-Code/schema.sql) | DDL PostGIS |
| [docs/Setup-Code/seed.sql](./docs/Setup-Code/seed.sql) | Data awal demo |
| [docs/Setup-Code/aggregator/fetch_bmkg.py](./docs/Setup-Code/aggregator/fetch_bmkg.py) | Implementasi prototipe aggregator |
| [docs/Setup-Code/aggregator/test_parse.py](./docs/Setup-Code/aggregator/test_parse.py) | Pengujian parser dan fallback |

## 6. Konvensi Kode & Pola

- Backend menggunakan skema Pydantic, service berbasis SQLAlchemy, type hints dan pytest dengan dependency/fake untuk tes offline.
- Dashboard memakai TypeScript, React Query untuk server state, hooks API dan komponen UI; styling utama menggunakan Tailwind/CSS.
- Aplikasi warga memakai Riverpod, repository Dio, model JSON, Hive untuk antrean offline dan `connectivity_plus` untuk auto-sync.
- REST API memakai prefiks `/v1`, enum status terdefinisi, timestamp UTC dan payload GeoJSON/WGS 84.
- Prototipe CLI BMKG pada `docs/Setup-Code/aggregator/` tetap menjadi referensi terpisah dan tidak menduplikasi modul di `backend/app/`.

## 7. Batasan & Pekerjaan Lanjutan

- `notification_stub.py` belum mengirim push FCM/APNs; konfigurasi kredensial produksi belum tersedia.
- Load test Locust tersedia sebagai skrip, tetapi belum menjadi bukti SLA atau kapasitas produksi.
- Tes backend memakai fake/mock untuk menjaga suite offline; deployment dan integrasi layanan PostgreSQL/Redis nyata tetap perlu diuji pada lingkungan target.
- Token operator, CORS, HTTPS, rahasia JWT, backup/retensi data, observability dan kebijakan privasi harus ditinjau sebelum deployment publik.
- Build aplikasi mobile dan dashboard telah divalidasi secara lokal; pengujian perangkat fisik, distribusi store, dan konektivitas produksi bukan bagian validasi lokal tersebut.
- `tinggi_genangan_cm` adalah estimasi software-based dari BMKG, laporan warga atau input Operator BPBD; sistem tidak menggunakan sensor fisik/IoT.
