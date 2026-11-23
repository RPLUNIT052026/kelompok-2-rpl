# 📋 User Story & Acceptance Criteria
**HyperEvac System** · Rekayasa Perangkat Lunak · Universitas Samudra

> [!NOTE]
> Dokumen ini memuat daftar *User Story* yang diturunkan dari kebutuhan fungsional (`FR-01` s.d. `FR-10`) dan *Use Case* (`UC1` s.d. `UC8`) pada pengembangan **HyperEvac System** menggunakan pendekatan *Spiral Model*.

## 1. Identifikasi Persona / Aktor

| Kode Aktor | Nama Aktor / Persona | Deskripsi Peran | Platform Utama |
| :--- | :--- | :--- | :--- |
| **ACT-01** | **Warga Area Rawan** | Masyarakat di kawasan rawan bencana (banjir/gempa) yang membutuhkan peringatan dini, peta bahaya, rute evakuasi aman, dan fitur pelaporan kondisi jalan (SOS). | Aplikasi Mobile (Flutter Android/iOS) |
| **ACT-02** | **Operator BPBD / Tim SAR** | Petugas pusat komando bencana yang memantau *Live Digital Twin*, memverifikasi laporan warga, serta membuka/memblokir ruas jalan secara manual. | Web Dashboard Command Center (React JS) |
| **ACT-03** | **Tim Maintainer / DevOps** | Administrator teknis yang memantau kesehatan *server*, ketersediaan konektor API BMKG/USGS, beban trafik, dan log sistem. | Cloud Console & Endpoint Monitoring |
| **ACT-04** | **DataAggregator (Layanan Internal — Background Scheduler)** | Komponen internal yang secara periodik menarik, menormalisasi, dan memvalidasi data cuaca serta gempa dari Sistem Eksternal BMKG (EXT-01) dan USGS (EXT-02). | Cloud Backend (Python FastAPI worker) |

---

## 2. Daftar User Story (Product Backlog)

| ID | Aktor | Epic | Pernyataan User Story | Prioritas (MoSCoW) | Story Points | Target Implementasi |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **US-01** | DataAggregator | Integrasi Data Bahaya | **Sebagai** DataAggregator, **saya ingin** menarik data cuaca ekstrem dan gempa bumi dari API BMKG & USGS secara periodik dengan mekanisme *retry* dan *cache*, **sehingga** sistem tetap memiliki informasi bahaya terbaru meskipun terjadi gangguan jaringan sementara (`FR-01`, `UC8`). | *Must Have* | 5 | Sprint 3 — Tahap 3A |
| **US-02** | DataAggregator | Integrasi Data Bahaya | **Sebagai** DataAggregator, **saya ingin** memvalidasi dan menormalisasi format data dari berbagai sumber API ke dalam skema geospasial standar, **sehingga** *Routing Engine* dan *Digital Twin* hanya memproses data yang akurat dan bebas anomali (`FR-02`, `UC8`). | *Must Have* | 5 | Sprint 3 — Tahap 3A |
| **US-03** | Warga Area Rawan | Peringatan Dini & Pemetaan | **Sebagai** Warga Area Rawan, **saya ingin** menerima *push notification* darurat secara *real-time* ketika wilayah RW saya memasuki ambang bahaya, **sehingga** saya dapat segera bersiap melakukan evakuasi lebih dini (`FR-03`, `UC2`). | *Must Have* | 5 | Sprint 3 — Tahap 3A |
| **US-04** | Warga Area Rawan | Peringatan Dini & Pemetaan | **Sebagai** Warga Area Rawan, **saya ingin** melihat peta interaktif yang menampilkan zona bahaya aktif dan titik kumpul aman di sekitar lokasi saya, **sehingga** saya mengetahui area mana yang harus dihindari (`FR-04`, `UC1`). | *Must Have* | 3 | Sprint 3 — Tahap 3A |
| **US-05** | Warga Area Rawan | Navigasi Evakuasi Pintar | **Sebagai** Warga Area Rawan, **saya ingin** mendapatkan rekomendasi rute evakuasi tercepat yang otomatis dihitung ulang ketika ada jalan terendam atau tertutup, **sehingga** saya tidak terjebak di jalur berbahaya (`FR-05`, `UC3`). | *Must Have* | 8 | Sprint 3 — Tahap 3A |
| **US-06** | Warga Area Rawan | Navigasi Evakuasi Pintar | **Sebagai** Warga Area Rawan, **saya ingin** diarahkan ke rute evakuasi alternatif yang terdistribusi secara proporsional (anti-*bottleneck*), **sehingga** tidak terjadi penumpukan massa dan kemacetan fatal di satu jalur evakuasi (`FR-09`, `UC3`). | *Should Have* | 8 | Sprint 3 — Tahap 3A |
| **US-07** | Warga Area Rawan | Crowd-Sensing (SOS) | **Sebagai** Warga Area Rawan, **saya ingin** melaporkan kondisi jalan yang tertutup atau aman beserta koordinat GPS melalui tombol SOS (termasuk saat *offline* melalui antrean lokal), **sehingga** warga lain dan petugas BPBD mengetahui kondisi lapangan terkini (`FR-06`, `UC4`). | *Should Have* | 5 | Sprint 3 — Tahap 3B |
| **US-08** | Operator BPBD / Tim SAR | Command Center & Verifikasi | **Sebagai** Operator BPBD, **saya ingin** memverifikasi laporan warga yang memiliki skor kepercayaan rendah serta memblokir atau membuka ruas jalan secara manual di peta, **sehingga** akurasi jalur evakuasi tetap terkendali oleh otoritas resmi (`FR-07`, `UC5`). | *Must Have* | 5 | Sprint 3 — Tahap 3B |
| **US-09** | Operator BPBD / Tim SAR | Command Center & Verifikasi | **Sebagai** Operator BPBD, **saya ingin** memantau visualisasi *Live Digital Twin* wilayah RW beserta estimasi sebaran warga terdampak, **sehingga** saya dapat mengambil keputusan pengerahan tim SAR secara tepat sasaran (`FR-08`, `UC6`). | *Should Have* | 8 | Sprint 3 — Tahap 3B |
| **US-10** | Tim Maintainer / DevOps | Observabilitas & Keandalan | **Sebagai** Tim Maintainer / DevOps, **saya ingin** memantau status kesehatan layanan (*health check*), latensi database PostGIS, usia *cache* BMKG/USGS, dan log trafik melalui *endpoint* khusus, **sehingga** kegagalan infrastruktur saat lonjakan bencana dapat segera dimitigasi (`FR-10`, `UC7`). | *Could Have* | 3 | Sprint 3 — Tahap 3A |

**Total Estimasi Story Points:** **55 Poin**. Sprint 1 dan Sprint 2 menyelesaikan analisis/desain dan prototipe aggregator; implementasi user story ditargetkan pada Sprint 3 (Tahap 3A Core API/Routing dan Tahap 3B Dashboard/SOS).

---

## 3. Rincian Acceptance Criteria (Given - When - Then)

### US-01 & US-02: Akuisisi, Validasi, dan Normalisasi Data Bahaya (`FR-01`, `FR-02`)
* **Kriteria 1 (Penarikan Normal):** *Given* jadwal penarikan periodik aktif, *When* sistem memanggil API BMKG/USGS dan merespons HTTP `200 OK`, *Then* data dinormalisasi ke skema internal dan disimpan ke tabel `Hazard`.
* **Kriteria 2 (Mekanisme Retry & Fallback Cache):** *Given* API BMKG/USGS mengalami *timeout* atau gagal diakses, *When* sistem mencoba ulang dengan *exponential backoff* hingga batas maksimum (3 kali) dan tetap gagal, *Then* sistem mengambil data dari Redis cache terakhir serta memberi penanda usia data (`data_kedaluwarsa = true`).
* **Kriteria 3 (Validasi Geospasial):** *Given* payload JSON/XML diterima dari API eksternal, *When* terdapat koordinat di luar batas wilayah atau nilai sensor tidak valid (`null`/negatif), *Then* sistem menolak entri cacat tersebut dan mencatat peringatan ke dalam log.

### US-03 & US-04: Notifikasi Darurat & Peta Bahaya Warga (`FR-03`, `FR-04`)
* **Kriteria 1 (Push Notification Berbasis Lokasi):** *Given* status bahaya suatu RW berubah menjadi `SIAGA` atau `AWAS`, *When* warga berada di dalam poligon terdampak, *Then* aplikasi mobile menampilkan *push notification* darurat dalam waktu `< 5 detik` beserta tombol pintas menuju rute evakuasi.
* **Kriteria 2 (Visualisasi Peta Zona Bahaya):** *Given* warga membuka aplikasi mobile, *When* halaman peta dimuat (`GET /v1/hazards`), *Then* peta menampilkan poligon zona bahaya berwarna sesuai tingkat keparahan (Kuning = Waspada, Oranye = Siaga, Merah = Awas) serta ikon lokasi titik kumpul.

### US-05 & US-06: Perhitungan Rute Evakuasi & Anti-Bottleneck (`FR-05`, `FR-09`)
* **Kriteria 1 (Kalkulasi Ulang Otomatis):** *Given* warga sedang bernavigasi menuju titik kumpul, *When* ruas jalan di depan ditandai tertutup akibat banjir atau blokir manual BPBD, *Then* *Routing Engine* menghitung ulang rute bebas bahaya secara otomatis dan memperbarui tampilan garis navigasi warga.
* **Kriteria 2 (Pemecahan Beban Rute / Anti-Bottleneck):** *Given* jumlah warga yang mengakses satu koridor jalan melebihi ambang kapasitas ruas (`RoadSegment`), *When* warga berikutnya meminta rute evakuasi (`GET /v1/routes/evacuation`), *Then* sistem mendistribusikan rekomendasi ke rute alternatif kedua/ketiga yang aman agar beban trafik merata.
* **Kriteria 3 (Tidak Ada Rute Aman):** *Given* seluruh ruas menuju titik kumpul berbahaya atau tertutup, *When* Routing Engine tidak menemukan rute aman, *Then* sistem mengembalikan instruksi **Evakuasi Vertikal** dan mengirim **Alert SAR**.

### US-07: Pelaporan Kondisi Jalan oleh Warga / SOS (`FR-06`)
* **Kriteria 1 (Pengiriman Laporan Online):** *Given* warga menekan tombol SOS di aplikasi, *When* warga memilih kategori (`tertutup` / `aman`) dan koneksi internet tersedia, *Then* aplikasi mengirim laporan (`POST /v1/reports`) beserta `device_id`, `segment_id`, koordinat `lat`/`lng`, dan `dibuat_pada`; jika `skor_kepercayaan >= 0.75` dan `tipe = tertutup`, ruas menjadi `TERTUTUP_SEMENTARA`, laporan berstatus `terverifikasi_otomatis`, dan rute dihitung ulang; selain itu laporan masuk antrean `MENUNGGU_TINJAUAN` dengan status `menunggu_tinjauan`.
* **Kriteria 2 (Antrean Offline Otomatis):** *Given* warga mengirim laporan SOS saat tidak ada sinyal internet, *When* tombol kirim ditekan, *Then* laporan disimpan di penyimpanan lokal perangkat dan otomatis dikirim ulang ke *server* begitu koneksi kembali tersedia.

### US-08 & US-09: Verifikasi BPBD, Blokir Manual, dan Live Digital Twin (`FR-07`, `FR-08`)
* **Kriteria 1 (Verifikasi & Penutupan Ruas Manual):** *Given* Operator BPBD masuk ke Web Dashboard, *When* operator membaca antrean (`GET /v1/admin/reports`), menerima/menolak laporan (`PATCH /v1/admin/reports/{id}`), atau memblokir/membuka ruas (`POST /v1/admin/routes/block`, `DELETE /v1/admin/routes/block/{segment_id}`), *Then* status laporan dan reputasi pelapor diperbarui; ruas manual menjadi `TERTUTUP_MANUAL` dengan `diblokir_manual = true`, dan perubahan yang memengaruhi keterlaluan jalan memicu kalkulasi ulang rute.
* **Kriteria 2 (Pemantauan Digital Twin):** *Given* Operator BPBD memilih wilayah RW tertentu (`GET /v1/twin/{rw_id}`), *When* dashboard memuat data spasial, *Then* layar menampilkan status tinggi genangan/bahaya terkini, daftar ruas jalan tertutup, dan estimasi jumlah warga di zona tersebut.

### US-10: Pemantauan Kesehatan Layanan (`FR-10`)
* **Kriteria 1 (Endpoint Health Check):** *Given* Tim Maintainer mengakses `GET /v1/health`, *When* layanan berjalan normal, *Then* sistem mengembalikan status koneksi PostgreSQL/PostGIS, Redis Cache, serta waktu penarikan terakhir API BMKG/USGS dalam format JSON.
