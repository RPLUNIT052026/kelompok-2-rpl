# 🔀 Activity Diagram (Berbasis Swimlane Aktor & Sistem)
**HyperEvac System** · Rekayasa Perangkat Lunak · Universitas Samudra

> [!NOTE]
> Sesuai arahan revisi pembimbing, dokumen **Activity Diagram** ini telah dipisahkan dari **Flowchart Algoritma Sistem** (`FLOWCHART.md`) dan dipecah menjadi diagram terpisah untuk setiap *Use Case* utama dengan menggunakan partisi **Swimlane** (*Aktor*, *Aplikasi Client*, dan *Backend Server*).

---

## 1. Activity Diagram: Penerimaan Peringatan Dini & Lihat Peta Bahaya (`UC1` & `UC2`)

Menggambarkan interaksi aktivitas antara **Warga Area Rawan**, **Aplikasi Mobile**, dan **Backend Server** saat terjadi peringatan dini bencana hingga warga melihat peta zona bahaya aktif.

```mermaid
flowchart TD
    subgraph Backend["⚙️ Backend Server HyperEvac"]
        B1([Deteksi Status Bahaya Baru di RW]) --> B2["Kirim Push Notification Darurat ke Warga di Zona Terdampak"]
        B5["Ambil Data Poligon Bahaya Aktif & Titik Kumpul (GET /v1/hazards)"] --> B6["Kirim Respons GeoJSON Zona Bahaya"]
    end

    subgraph Mobile["📱 Aplikasi Mobile (Flutter)"]
        M1["Terima & Tampilkan Notifikasi Peringatan Dini di Layar"]
        M2["Muat Antarmuka Peta Interaktif & Request Data Hazard"]
        M3["Render Poligon Zona Bahaya (Kuning/Oranye/Merah) & Titik Kumpul"]
    end

    subgraph Warga["👤 Warga Area Rawan"]
        W1["Membuka Notifikasi Darurat / Membuka Aplikasi"]
        W2["Melihat Peta Zona Bahaya & Memilih Titik Kumpul"]
        W3([Selesai])
    end

    B2 --> M1
    M1 --> W1
    W1 --> M2
    M2 --> B5
    B6 --> M3
    M3 --> W2
    W2 --> W3
```

---

## 2. Activity Diagram: Navigasi Rute Evakuasi & Anti-Bottleneck (`UC3`)

Menggambarkan alur aktivitas terpisah khusus untuk permintaan navigasi rute evakuasi aman beserta pengalihan rute otomatis apabila jalur di depan tertutup atau padat.

```mermaid
flowchart TD
    subgraph Warga["👤 Warga Area Rawan"]
        W1([Mulai Navigasi]) --> W2["Tekan Tombol 'Cari Rute Evakuasi Aman'"]
        W3["Mengikuti Panduan Arah Rute di Peta"]
        W4([Tiba di Titik Kumpul Aman])
    end

    subgraph Mobile["📱 Aplikasi Mobile (Flutter)"]
        M1["Ambil Koordinat GPS Warga Saat Ini"]
        M2["Kirim Request GET /v1/routes/evacuation"]
        M3["Tampilkan Garis Rute Utama & Alternatif beserta Estimasi Waktu"]
        M4{"Ada Perubahan Status Jalan Selama Navigasi?"}
        M5["Perbarui Garis Rute & Tampilkan Peringatan Pengalihan Jalur"]
    end

    subgraph Backend["⚙️ Backend Routing Engine"]
        B1["Evaluasi Ruas Jalan Aman & Beban Kapasitas (Anti-Bottleneck)"]
        B2["Kembalikan Rekomendasi Rute Optimal ke Aplikasi"]
        B3["Kirim Event Pembaruan Rute Real-Time"]
    end

    W2 --> M1
    M1 --> M2
    M2 --> B1
    B1 --> B2
    B2 --> M3
    M3 --> W3
    W3 --> M4
    M4 -- "Ya (Rute Diblokir/Banjir)" --> B3
    B3 --> M5
    M5 --> W3
    M4 -- "Tidak" --> W4
```

---

## 3. Activity Diagram: Pelaporan Kondisi Jalan / Tombol SOS oleh Warga (`UC4`)

Menggambarkan alur aktivitas warga saat melaporkan kondisi jalan tertutup atau aman di lapangan, termasuk penanganan kondisi *offline*.

```mermaid
flowchart TD
    subgraph Warga["👤 Warga Area Rawan"]
        W1([Menemukan Jalan Banjir / Tertutup]) --> W2["Tekan Tombol SOS / Lapor Kondisi Jalan"]
        W3["Pilih Kategori Laporan (Jalan Tertutup / Jalan Aman) & Kirim"]
        W4([Selesai])
    end

    subgraph Mobile["📱 Aplikasi Mobile (Flutter)"]
        M1["Tampilkan Form Cepat Laporan SOS & Ambil Titik GPS"]
        M2{"Koneksi Internet Tersedia?"}
        M3["Simpan Laporan di Antrean Lokal Perangkat (Offline Queue)"]
        M4["Kirim Payload Laporan (POST /v1/reports) Saat Online"]
        M5["Tampilkan Konfirmasi Status Laporan Diterima"]
    end

    subgraph Backend["⚙️ Backend Server HyperEvac"]
        B1["Terima Laporan & Hitung Trust Score Pelapor"]
        B2{"Trust Score >= Ambang Batas?"}
        B3["Tandai Ruas Jalan Sementara & Picu Hitung Ulang Rute"]
        B4["Masukkan ke Antrean Verifikasi Operator BPBD"]
        B5["Kirim Respons HTTP 201 Created"]
    end

    W2 --> M1
    M1 --> W3
    W3 --> M2
    M2 -- "Tidak" --> M3
    M3 --> M4
    M2 -- "Ya" --> M4
    M4 --> B1
    B1 --> B2
    B2 -- "Ya" --> B3
    B2 -- "Tidak" --> B4
    B3 --> B5
    B4 --> B5
    B5 --> M5
    M5 --> W4
```

---

## 4. Activity Diagram: Verifikasi Laporan & Pemblokiran Rute Manual oleh BPBD (`UC5` & `UC6`)

Menggambarkan alur aktivitas **Operator BPBD** pada **Web Dashboard Command Center** saat memantau *Live Digital Twin*, memverifikasi laporan warga, serta memblokir/membuka ruas jalan secara manual.

```mermaid
flowchart TD
    subgraph Operator["👮 Operator BPBD / Tim SAR"]
        O1([Login ke Command Center]) --> O2["Pilih Wilayah RW untuk Memantau Live Digital Twin"]
        O3{"Tindakan Operator?"}
        O4["Tinjau Antrean Laporan Warga & Pilih Valid / Tolak"]
        O5["Klik Ruas Jalan di Peta & Pilih Blokir / Buka Rute Manual"]
        O6([Selesai])
    end

    subgraph Dashboard["💻 Web Dashboard (React JS)"]
        D1["Request Data Digital Twin (GET /v1/twin/{rw_id})"]
        D2["Tampilkan Peta 2D/3D Digital Twin, Sebaran Warga & Antrean Laporan"]
        D3["Kirim Keputusan Verifikasi Laporan ke Server"]
        D4["Kirim Request POST / DELETE /v1/admin/routes/block"]
        D5["Perbarui Visualisasi Status Ruas Jalan di Dashboard"]
    end

    subgraph Backend["⚙️ Backend Server HyperEvac"]
        B1["Ambil Status Spasial RW, Hazard & Ruas Jalan dari PostGIS"]
        B2["Perbarui Status Laporan & Sesuaikan Skor Reputasi Pelapor"]
        B3["Ubah Status RoadSegment (BLOCKED / OPEN) di Database"]
        B4["Hitung Ulang Rute Evakuasi & Broadcast Notifikasi ke Warga Terdampak"]
    end

    O2 --> D1
    D1 --> B1
    B1 --> D2
    D2 --> O3
    O3 -- "Verifikasi Laporan SOS" --> O4
    O4 --> D3
    D3 --> B2
    B2 --> B3
    O3 -- "Blokir / Buka Jalan Manual" --> O5
    O5 --> D4
    D4 --> B3
    B3 --> B4
    B4 --> D5
    D5 --> O6
```

---

## 5. Activity Diagram: Pemantauan Kesehatan Layanan & Log oleh Tim Maintainer (`UC7`)

Menggambarkan alur aktivitas **Tim Maintainer** dalam memantau ketersediaan layanan (*high availability*), status *cache* API BMKG/USGS, dan performa database.

```mermaid
flowchart TD
    subgraph Maintainer["🛠️ Tim Maintainer / DevOps"]
        T1([Mulai Pemantauan]) --> T2["Buka Dashboard Monitoring / Panggil Endpoint Health"]
        T3{"Ada Komponen Degraded / Error?"}
        T4["Periksa Log Error & Lakukan Restart / Scaling Layanan"]
        T5([Selesai Pemantauan])
    end

    subgraph Console["🖥️ Cloud Console & Monitoring"]
        C1["Kirim Request GET /v1/health"]
        C2["Tampilkan Metrik Status PostGIS, Redis Cache & Usia Data BMKG"]
    end

    subgraph Backend["⚙️ Backend Server HyperEvac"]
        B1["Cek Koneksi Pool PostGIS, Ping Redis & Cek Timestamp DataAggregator"]
        B2["Kembalikan Payload JSON Status Kesehatan Sistem"]
    end

    T2 --> C1
    C1 --> B1
    B1 --> B2
    B2 --> C2
    C2 --> T3
    T3 -- "Ya" --> T4
    T4 --> T5
    T3 -- "Tidak (Semua Sehat)" --> T5
```
