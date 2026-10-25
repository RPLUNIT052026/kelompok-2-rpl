# 🔄 Flowchart Sistem & Algoritma Inti
**HyperEvac System** · Rekayasa Perangkat Lunak · Universitas Samudra

> [!NOTE]
> Dokumen ini memisahkan **Flowchart Algoritma & Pemrosesan Sistem** dari **Activity Diagram**. Flowchart di bawah ini berfokus pada logika prosedural, percabangan komputasi, struktur perulangan (*loop*), serta pengolahan input/output di sisi mesin (*engine*), sedangkan interaksi lintas-aktor (*swimlane*) didokumentasikan secara terpisah pada berkas `ACTIVITY-DIAGRAM.md`.

---

## 1. Flowchart Algoritma Akuisisi, Validasi & Fallback Cache API (`DataAggregator`)

Menggambarkan alur logika internal *background worker* saat menarik data cuaca/gempa dari BMKG & USGS, termasuk mekanisme *exponential backoff retry* dan *fallback* ke *cache* lokal apabila API eksternal mengalami gangguan.

```mermaid
flowchart TD
    Start([Mulai Siklus Scheduler]) --> Init["Inisialisasi variabel retry_count = 0, max_retry = 3"]
    Init --> Fetch[/"Request HTTP GET ke Endpoint API BMKG & USGS"/]
    Fetch --> CheckHTTP{"Respons HTTP == 200 OK?"}

    CheckHTTP -- "Tidak (Timeout / Error 5xx)" --> IncRetry["retry_count = retry_count + 1"]
    IncRetry --> CheckMax{"retry_count <= max_retry?"}
    CheckMax -- "Ya" --> WaitBackoff["Tunggu jeda Exponential Backoff (2^retry_count detik)"]
    WaitBackoff --> Fetch
    CheckMax -- "Tidak (Melewati Batas)" --> ReadCache[/"Ambil data terakhir dari Redis / Local Cache"/]
    ReadCache --> FlagStale["Set atribut stale_data_flag = TRUE & hitung usia cache"]
    FlagStale --> ParseData

    CheckHTTP -- "Ya" --> ParseData["Parsing payload JSON/XML & Normalisasi Skema Geospasial"]
    ParseData --> ValidateSchema{"Koordinat & Nilai Sensor Valid?"}
    ValidateSchema -- "Tidak" --> LogError[/"Catat Error Anomali Data ke System Log"/]
    LogError --> EndCycle([Selesai Siklus])

    ValidateSchema -- "Ya" --> SaveDB[("Simpan / Update Tabel Hazard & DigitalTwin di PostGIS")]
    SaveDB --> CheckThreshold{"Nilai Bahaya >= Ambang Siaga/Awas?"}
    CheckThreshold -- "Tidak" --> EndCycle
    CheckThreshold -- "Ya" --> TriggerEngine[["Panggil Sub-Proses: Routing Engine & Push Notification"]]
    TriggerEngine --> EndCycle
```

---

## 2. Flowchart Algoritma Perhitungan Rute Dinamis & Anti-Bottleneck (`Routing Engine`)

Menggambarkan logika komputasi spasial di PostGIS dalam memotong ruas jalan yang terendam/diblokir dan mendistribusikan warga ke beberapa rute alternatif agar tidak terjadi penumpukan (*traffic bottleneck*).

```mermaid
flowchart TD
    Start([Mulai Kalkulasi Rute]) --> InputParam[/"Input: Koordinat Warga (origin), ID RW, & Daftar Poligon Hazard Aktif"/]
    InputParam --> LoadGraph[/"Muat Graf Jaringan Jalan (RoadSegment) dari PostGIS"/]
    LoadGraph --> SpatialIntersect["Lakukan operasi ST_Intersects(RoadSegment.geom, Hazard.polygon)"]
    SpatialIntersect --> FilterRoad{"Ruas Jalan Terkena Bahaya atau Diblokir Manual?"}

    FilterRoad -- "Ya" --> ExcludeEdge["Set bobot ruas (edge cost) = INFINITY (Nonaktifkan Ruas)"]
    FilterRoad -- "Tidak" --> CalcWeight["Hitung bobot dasar: cost = panjang_jalan / kecepatan_rata_rata"]
    ExcludeEdge --> FindKPaths
    CalcWeight --> FindKPaths

    FindKPaths["Jalankan algoritma K-Shortest Paths (Yen's / Dijkstra) menuju Titik Kumpul Aman"] --> FoundCheck{"Ditemukan minimal 1 rute aman?"}
    FoundCheck -- "Tidak" --> ReturnEmergency[/"Output: Instruksi Evakuasi Vertikal / Titik Darurat Terdekat + Alert SAR"/]
    ReturnEmergency --> EndRoute([Selesai])

    FoundCheck -- "Ya" --> CheckCapacity{"Beban pengguna pada Rute Utama > 80% kapasitas ruas?"}
    CheckCapacity -- "Tidak" --> AssignPrimary["Tetapkan Rute Utama (Rute 1) untuk pengguna"]
    CheckCapacity -- "Ya (Potensi Bottleneck)" --> AssignAlt["Alihkan ke Rute Alternatif (Rute 2 / Rute 3) dengan beban terendah"]

    AssignPrimary --> UpdateLoad[("Inkrementasi counter active_users pada RoadSegment terpilih")]
    AssignAlt --> UpdateLoad
    UpdateLoad --> OutputGeoJSON[/"Output: Payload GeoJSON Rute Utama, Rute Alternatif & Estimasi Waktu"/]
    OutputGeoJSON --> EndRoute
```

---

## 3. Flowchart Algoritma Evaluasi *Trust Score* Laporan Warga (`Crowd-Sensing SOS`)

Menggambarkan logika perhitungan skor kepercayaan laporan kondisi jalan dari warga untuk menentukan apakah ruas jalan langsung ditandai otomatis atau masuk ke antrean verifikasi manual BPBD.

```mermaid
flowchart TD
    Start([Mulai Evaluasi Laporan SOS]) --> InputSOS[/"Input: user_id, koordinat_gps, jenis_laporan (Tertutup/Aman), timestamp"/]
    InputSOS --> CheckDistance["Hitung jarak GPS pelapor terhadap geometri RoadSegment terdekat"]
    CheckDistance --> ValidProximity{"Jarak GPS <= 50 meter dari ruas jalan?"}

    ValidProximity -- "Tidak (Lokasi Terlalu Jauh)" --> PenaltyDist["Faktor Kedekatan (W_prox) = 0.2"]
    ValidProximity -- "Ya" --> FullDist["Faktor Kedekatan (W_prox) = 1.0"]

    PenaltyDist --> CountCorroboration
    FullDist --> CountCorroboration

    CountCorroboration["Hitung jumlah laporan serupa pada ruas yang sama dalam 15 menit terakhir (N_cluster)"] --> CalcScore["Hitung Trust Score = (0.4 * Reputasi_User) + (0.3 * W_prox) + (0.3 * min(N_cluster / 3, 1.0))"]
    CalcScore --> SaveReport[("Simpan laporan ke tabel RoadReport beserta nilai Trust Score")]
    SaveReport --> CheckScore{"Trust Score >= 0.75?"}

    CheckScore -- "Ya (Kepercayaan Tinggi)" --> AutoMark[("Ubah status RoadSegment menjadi TEMPORARY_CLOSED secara otomatis")]
    AutoMark --> TriggerReroute[["Picu Kalkulasi Ulang Rute untuk Warga di Sekitar"]]
    TriggerReroute --> EndSOS([Selesai])

    CheckScore -- "Tidak (Perlu Tinjauan)" --> QueueBPBD[("Masukkan laporan ke Antrean Verifikasi Manual Dashboard BPBD")]
    QueueBPBD --> EndSOS
```
