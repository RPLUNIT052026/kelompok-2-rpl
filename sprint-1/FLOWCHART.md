# 🔄 Flowchart Sistem & Algoritma Inti
**HyperEvac System** · Rekayasa Perangkat Lunak · Universitas Samudra

> [!NOTE]
> Flowchart ini mendokumentasikan rancangan algoritma target Sprint 3. Prototipe Sprint 1 saat ini hanya mengimplementasikan aggregator BMKG dengan cache lokal.

## 1. Akuisisi, Validasi & Fallback Cache API (`DataAggregator`)

```mermaid
flowchart TD
    Start([Mulai Siklus Scheduler]) --> Init["Inisialisasi retry_count = 0, max_retry = 3"]
    Init --> Fetch[/"Request HTTP GET ke API BMKG & USGS"/]
    Fetch --> CheckHTTP{"Respons HTTP == 200 OK?"}
    CheckHTTP -- "Tidak (Timeout / Error Non-200)" --> IncRetry["retry_count = retry_count + 1"]
    IncRetry --> CheckMax{"retry_count < max_retry?"}
    CheckMax -- "Ya" --> WaitBackoff["Tunggu exponential backoff"]
    WaitBackoff --> Fetch
    CheckMax -- "Tidak" --> ReadCache[/"Ambil payload terakhir dari Redis Cache"/]
    ReadCache --> FlagStale["Set data_kedaluwarsa = true dan hitung usia cache"]
    FlagStale --> ParseData["Parsing dan normalisasi payload"]
    CheckHTTP -- "Ya" --> ParseData
    ParseData --> ValidateSchema{"Skema, koordinat & nilai valid?"}
    ValidateSchema -- "Tidak" --> LogError[/"Catat anomali ke system log"/]
    LogError --> EndCycle([Selesai Siklus])
    ValidateSchema -- "Ya" --> SaveDB[("Simpan / perbarui Hazard di PostGIS")]
    SaveDB --> UpdateCache[("Update Redis Cache & set data_kedaluwarsa = false")]
    UpdateCache --> CheckThreshold{"level_bahaya >= SIAGA?"}
    CheckThreshold -- "Tidak" --> EndCycle
    CheckThreshold -- "Ya" --> TriggerEngine[["Panggil Digital Twin Engine, Routing Engine & Push Notification"]]
    TriggerEngine --> EndCycle
```

## 2. Perhitungan Rute Dinamis & Anti-Bottleneck (`RoutingEngine`)

```mermaid
flowchart TD
    Start([Mulai Kalkulasi Rute]) --> InputParam[/"Input origin, rw_id & Hazard aktif"/]
    InputParam --> LoadGraph[/"Muat RoadSegment dari PostGIS"/]
    LoadGraph --> SpatialIntersect["ST_Intersects(RoadSegment.geometri, Hazard.geometri)"]
    SpatialIntersect --> FilterRoad{"Ruas terdampak atau ditutup?"}
    FilterRoad -- "Ya" --> ExcludeEdge["Nonaktifkan ruas: edge cost = INFINITY"]
    FilterRoad -- "Tidak" --> CalcWeight["Hitung cost = panjang_m / kecepatan_rata_rata_mps"]
    ExcludeEdge --> FindKPaths["Cari K shortest paths ke titik_kumpul"]
    CalcWeight --> FindKPaths
    FindKPaths --> FoundCheck{"Ditemukan rute aman?"}
    FoundCheck -- "Tidak" --> ReturnEmergency[/"Instruksi Evakuasi Vertikal + Alert SAR"/]
    ReturnEmergency --> EndRoute([Selesai])
    FoundCheck -- "Ya" --> CheckCapacity{"pengguna_aktif > 0.8 * kapasitas_maks?"}
    CheckCapacity -- "Tidak" --> AssignPrimary["Tetapkan rute utama"]
    CheckCapacity -- "Ya (bottleneck)" --> AssignAlt["Pilih rute alternatif dengan beban terendah"]
    AssignPrimary --> UpdateLoad[("Perbarui pengguna_aktif pada RoadSegment terpilih")]
    AssignAlt --> UpdateLoad
    UpdateLoad --> OutputGeoJSON[/"Keluarkan GeoJSON rute utama/alternatif dan estimasi waktu"/]
    OutputGeoJSON --> EndRoute
```

## 3. Evaluasi Trust Score Laporan Warga (`RoadReport`)

Laporan berkepercayaan tinggi hanya dapat menutup ruas secara otomatis jika tipenya `tertutup`. Laporan `aman` tidak membuka ruas tanpa verifikasi BPBD.

```mermaid
flowchart TD
    Start([Mulai Evaluasi Laporan]) --> InputSOS[/"Input device_id, segment_id, lat, lng, tipe (tertutup/aman), dibuat_pada"/]
    InputSOS --> CheckDistance["Hitung jarak ke geometri RoadSegment terdekat"]
    CheckDistance --> ValidProximity{"Jarak <= 50 meter?"}
    ValidProximity -- "Tidak" --> PenaltyDist["W_prox = 0.2"]
    ValidProximity -- "Ya" --> FullDist["W_prox = 1.0"]
    PenaltyDist --> CountCorroboration["Hitung laporan serupa pada ruas dalam 15 menit"]
    FullDist --> CountCorroboration
    CountCorroboration --> CalcScore["Hitung skor_kepercayaan = (0.4 * PerangkatWarga.reputasi) + (0.3 * W_prox) + (0.3 * min(N_cluster / 3, 1.0))"]
    CalcScore --> SaveReport[("Simpan RoadReport dan skor_kepercayaan")]
    SaveReport --> CheckScore{"skor_kepercayaan >= 0.75?"}
    CheckScore -- "Ya" --> CheckType{"tipe == tertutup?"}
    CheckType -- "Ya" --> AutoMark[("RoadSegment.status = TERTUTUP_SEMENTARA; RoadReport.status = terverifikasi_otomatis")]
    AutoMark --> TriggerReroute[["Picu kalkulasi ulang Routing Engine"]]
    TriggerReroute --> EndSOS([Selesai])
    CheckType -- "Tidak (aman)" --> QueueBPBD[("Set RoadReport.status = menunggu_tinjauan; antrekan BPBD")]
    CheckScore -- "Tidak" --> QueueBPBD
    QueueBPBD --> EndSOS
```
