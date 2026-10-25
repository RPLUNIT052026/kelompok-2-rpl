# 🧮 Analisis & Perhitungan Function Point (FP)
**HyperEvac System** · Rekayasa Perangkat Lunak · Universitas Samudra

> [!NOTE]
> Dokumen ini menyajikan estimasi ukuran perangkat lunak, kompleksitas fungsional, dan beban kerja (*effort*) untuk pengembangan **HyperEvac System** menggunakan metode **Function Point Analysis (FPA)** standar Albrecht / IFPUG.

---

## 1. Identifikasi Komponen Fungsional (CFP / UFP)

Perhitungan *Crude/Unadjusted Function Point (UFP)* dibagi ke dalam 5 kategori komponen fungsional berdasarkan dokumen `USE-CASE.md`, `API-SPEC.md`, dan `CLASS-DAN-DATABASE.md`:

### A. Internal Logical Files (ILF)
Berkas logika internal / tabel basis data utama yang dikelola di dalam klaster **PostgreSQL + PostGIS** milik sistem:

| Kode | Nama Tabel / Entitas (`CLASS-DAN-DATABASE.md`) | Deskripsi Data yang Dikelola | Kompleksitas | Bobot |
| :--- | :--- | :--- | :---: | :---: |
| **ILF-01** | `RW` | Data wilayah administrasi RW, batas poligon wilayah, dan koordinat titik kumpul aman. | *Simple* | 7 |
| **ILF-02** | `Hazard` | Data bencana aktif (banjir/gempa), geometri area terdampak, tingkat keparahan, dan cap waktu. | *Average* | 10 |
| **ILF-03** | `DigitalTwin` | Status simulasi kembaran digital per RW, tinggi genangan, dan estimasi warga terdampak. | *Average* | 10 |
| **ILF-04** | `RoadSegment` | Data geospasial ruas jalan (*linestring*), kapasitas beban jalan, dan status buka/tutup. | *Average* | 10 |
| **ILF-05** | `EvacuationRoute` | Data rute evakuasi utama dan rute alternatif hasil perhitungan *Routing Engine*. | *Average* | 10 |
| **ILF-06** | `RoadReport` | Data laporan kondisi jalan (*crowd-sensing* SOS) dari warga beserta skor kepercayaan. | *Simple* | 7 |
| | **Subtotal ILF** | **6 Entitas Basis Data Internal** | | **54** |

### B. External Interface Files (EIF)
Sumber data referensi eksternal yang dibaca oleh sistem (`DataAggregator`) namun dikelola oleh pihak ketiga:

| Kode | Nama Antarmuka Eksternal | Deskripsi Sumber Data | Kompleksitas | Bobot |
| :--- | :--- | :--- | :---: | :---: |
| **EIF-01** | `BMKG Weather & Flood Warning API` | Data prakiraan cuaca ekstrem, curah hujan, dan peringatan dini banjir dari BMKG. | *Average* | 7 |
| **EIF-02** | `USGS / BMKG Earthquake GeoJSON Feed` | Data parameter gempa bumi *real-time* (magnitudo, episentrum, kedalaman). | *Average* | 7 |
| | **Subtotal EIF** | **2 Antarmuka Data Eksternal** | | **14** |

### C. External Inputs (EI)
Proses transaksi masukan dari pengguna maupun *worker* yang menambah atau mengubah data pada ILF:

| Kode | Nama Proses Input / Endpoint | Aktor Pemicu | Kompleksitas | Bobot |
| :--- | :--- | :--- | :---: | :---: |
| **EI-01** | Kirim Laporan Kondisi Jalan / Tombol SOS (`POST /v1/reports` · `FR-06`) | Warga Area Rawan | *Average* | 4 |
| **EI-02** | Pemblokiran Ruas Jalan Manual (`POST /v1/admin/routes/block` · `FR-07`) | Operator BPBD | *Simple* | 3 |
| **EI-03** | Pembukaan Kembali Ruas Jalan (`DELETE /v1/admin/routes/block` · `FR-07`) | Operator BPBD | *Simple* | 3 |
| **EI-04** | Verifikasi Laporan Warga (Terima/Tolak Laporan di Dashboard · `FR-07`) | Operator BPBD | *Average* | 4 |
| **EI-05** | Ingesti, Validasi & Normalisasi Data Bahaya Otomatis (`FR-01`, `FR-02`) | Sistem Aggregator | *Complex* | 6 |
| | **Subtotal EI** | **5 Transaksi Input** | | **20** |

### D. External Outputs (EO)
Proses keluaran yang melibatkan perhitungan matematis, simulasi geospasial, atau logika algoritma turunan sebelum ditampilkan:

| Kode | Nama Proses Output / Endpoint | Logika Pemrosesan & Kalkulasi | Kompleksitas | Bobot |
| :--- | :--- | :--- | :---: | :---: |
| **EO-01** | Rekomendasi Rute Evakuasi & Anti-Bottleneck (`GET /v1/routes/evacuation` · `FR-05`, `FR-09`) | Kalkulasi graf jalur terpendek bebas bahaya + pemecahan beban trafik ke rute alternatif. | *Complex* | 7 |
| **EO-02** | Pengiriman *Push Notification* Darurat Berbasis Lokasi (`FR-03`) | Evaluasi *geofencing* poligon bahaya terhadap posisi warga dan pengiriman payload darurat. | *Average* | 5 |
| **EO-03** | Visualisasi Simulasi *Live Digital Twin* (`GET /v1/twin/{rw_id}` · `FR-08`) | Agregasi status bahaya RW, jumlah ruas jalan tertutup, dan estimasi warga terdampak. | *Complex* | 7 |
| **EO-04** | Kalkulasi *Trust Score* Laporan Crowd-Sensing (`FR-06`) | Perhitungan bobot reputasi pelapor dan konsistensi jarak spasial antar-laporan. | *Average* | 5 |
| | **Subtotal EO** | **4 Proses Output Berbasis Kalkulasi** | | **24** |

### E. External Inquiries (EQ)
Proses pencarian atau pengambilan data langsung (*retrieval*) tanpa mengubah ILF dan tanpa kalkulasi matematis turunan yang kompleks:

| Kode | Nama Proses Inquiry / Endpoint | Aktor Pengguna | Kompleksitas | Bobot |
| :--- | :--- | :--- | :---: | :---: |
| **EQ-01** | Lihat Daftar Bahaya Aktif & Peta Zona RW (`GET /v1/hazards` · `FR-04`) | Warga & BPBD | *Average* | 4 |
| **EQ-02** | Cek Status Kesehatan Layanan, Trafik & Log (`GET /v1/health` · `FR-10`) | Tim Maintainer | *Simple* | 3 |
| **EQ-03** | Lihat Daftar Antrean Laporan Warga di Web Dashboard (`FR-07`) | Operator BPBD | *Simple* | 3 |
| | **Subtotal EQ** | **3 Proses Inquiry** | | **10** |

---

## 2. Rekapitulasi Unadjusted Function Point (UFP / CFP)

| Kategori Komponen | Simple (Jml × Bobot) | Average (Jml × Bobot) | Complex (Jml × Bobot) | Total Poin |
| :--- | :---: | :---: | :---: | :---: |
| **Internal Logical Files (ILF)** | 2 × 7 = 14 | 4 × 10 = 40 | 0 × 15 = 0 | **54** |
| **External Interface Files (EIF)** | 0 × 5 = 0 | 2 × 7 = 14 | 0 × 10 = 0 | **14** |
| **External Inputs (EI)** | 2 × 3 = 6 | 2 × 4 = 8 | 1 × 6 = 6 | **20** |
| **External Outputs (EO)** | 0 × 4 = 0 | 2 × 5 = 10 | 2 × 7 = 14 | **24** |
| **External Inquiries (EQ)** | 2 × 3 = 6 | 1 × 4 = 4 | 0 × 6 = 0 | **10** |
| **Total UFP (Crude Function Point)** | | | | **122** |

---

## 3. Perhitungan Faktor Kompleksitas Teknis (GSC & VAF)

Penilaian **14 Karakteristik Sistem Umum (*General System Characteristics* / GSC)** diberikan dengan skala **0** (tidak berpengaruh) hingga **5** (sangat krusial/berpengaruh kuat) sesuai sifat **HyperEvac** sebagai *Safety-Critical System*:

| No | Karakteristik Sistem (GSC) | Nilai ($F_i$) | Justifikasi Teknis pada HyperEvac System |
| :---: | :--- | :---: | :--- |
| 1 | *Data Communications* | **5** | Komunikasi intensif melalui REST API, *push notification*, dan sinkronisasi data *real-time* antara Mobile, Web, dan Server. |
| 2 | *Distributed Data Processing* | **4** | Pemrosesan terdistribusi antara *Aggregator Worker*, *Routing Engine*, *Database Cluster*, dan *Cache Server*. |
| 3 | *Performance* | **5** | Kriteria *Safety-Critical*: waktu respons perhitungan rute dan peringatan dini harus sangat cepat saat darurat. |
| 4 | *Heavily Used Configuration* | **3** | Berjalan di atas *cloud container* dengan pembagian beban (*Load Balancer*). |
| 5 | *Transaction Rate* | **4** | Trafik transaksi melonjak tajam secara serentak ketika terjadi peringatan bencana di wilayah padat penduduk. |
| 6 | *Online Data Entry* | **4** | Input laporan warga (SOS) dari *smartphone* dan kendali blokir jalan interaktif oleh operator BPBD. |
| 7 | *End-User Efficiency* | **4** | Antarmuka dirancang khusus untuk kondisi darurat (tombol SOS satu sentuhan & peta navigasi kontras tinggi). |
| 8 | *Online Update* | **4** | Pembaruan status ruas jalan, zona bahaya, dan *Digital Twin* dilakukan secara *real-time* (*online*). |
| 9 | *Complex Processing* | **5** | Melibatkan kueri geospasial PostGIS, algoritma *multi-path routing* anti-*bottleneck*, dan perhitungan *Trust Score*. |
| 10 | *Reusability* | **3** | Modul API Engine dan komponen antarmuka dapat digunakan ulang untuk berbagai wilayah RW/kabupaten. |
| 11 | *Installation Ease* | **3** | Orkestrasi lingkungan menggunakan `docker-compose.yml` untuk memudahkan *deployment*. |
| 12 | *Operational Ease* | **4** | Dilengkapi mekanisme *auto-retry backoff*, *fallback cache* saat API eksternal mati, dan *endpoint health check*. |
| 13 | *Multiple Sites* | **3** | Mendukung multi-wilayah RW serta multi-platform (*Mobile Android/iOS* dan *Web Dashboard*). |
| 14 | *Facilitate Change* | **4** | Arsitektur modular berbasis *Spiral Model* memudahkan iterasi penambahan fitur per siklus. |
| | **Total Degree of Influence (TDI / $\sum F_i$)** | **55** | **Dari skor maksimum 70** |

### Rumus Value Adjustment Factor (VAF / TCF)
$$\text{VAF} = 0.65 + (0.01 \times \sum_{i=1}^{14} F_i)$$
$$\text{VAF} = 0.65 + (0.01 \times 55) = 0.65 + 0.55 = \mathbf{1.20}$$

---

## 4. Perhitungan Adjusted Function Point (AFP) & Estimasi Proyek

### A. Nilai Akhir Function Point (AFP)
$$\text{AFP} = \text{UFP} \times \text{VAF}$$
$$\text{AFP} = 122 \times 1.20 = \mathbf{146.40\text{ FP}}$$

### B. Estimasi Ukuran Baris Kode (*Lines of Code* / LOC)
Dengan menggunakan rata-rata konversi bahasa pemrograman modern pada *stack* proyek (**Python, Node.js, Dart/Flutter, dan React/JavaScript** $\approx 40\text{ LOC/FP}$):
$$\text{Estimasi LOC} = 146.40\text{ FP} \times 40\text{ LOC/FP} \approx \mathbf{5.856\text{ LOC}}\ (\pm 5,86\text{ KLOC})$$

### C. Estimasi Effort (Jam Orang) & Durasi Pengembangan
Dengan asumsi produktivitas tim pengembang akademik (4 anggota) sebesar **6 jam kerja per Function Point**:
* **Total Effort Pengembangan:** $146.40\text{ FP} \times 6\text{ jam/FP} = \mathbf{878,4\text{ Jam Orang (Person-Hours)}}$
* **Kapasitas Tim (4 Anggota × 18 jam/minggu):** $72\text{ Jam/Minggu}$
* **Estimasi Durasi Kalender:** $\frac{878,4\text{ Jam}}{72\text{ Jam/Minggu}} \approx \mathbf{12,2\text{ Minggu}}$ (terbagi ke dalam **2 Siklus/Sprint Spiral** @ 6 minggu per siklus, sesuai jadwal 1 semester perkuliahan).
