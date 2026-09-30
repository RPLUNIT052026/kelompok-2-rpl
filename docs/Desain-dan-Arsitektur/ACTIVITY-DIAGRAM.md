<div align="center">

![Dokumen](https://img.shields.io/badge/DOKUMEN-ACTIVITY_DIAGRAM-00f0ff?style=for-the-badge&labelColor=0b1020)
![Status](https://img.shields.io/badge/STATUS-RANCANGAN-7b5cff?style=for-the-badge&labelColor=0b1020)

# 🔀 Activity Diagram

**HyperEvac System** · Rekayasa Perangkat Lunak · Universitas Samudra

</div>

<img src="../docs/assets/divider.svg" width="100%" alt=""/>

> [!NOTE]
> Diagram aktivitas digambar dengan *flowchart* Mermaid (persegi = aktivitas, belah ketupat = keputusan).

## 1. Alur Utama: Dari Deteksi Bahaya sampai Warga Menerima Rute

```mermaid
flowchart TD
    A([Mulai]) --> B["Aggregator menarik data BMKG/USGS"]
    B --> C{"Pemanggilan API berhasil?"}
    C -- "Tidak" --> D["Coba ulang dengan backoff"]
    D --> E{"Masih gagal setelah batas percobaan?"}
    E -- "Ya" --> F["Pakai cache terakhir + tandai usia data"]
    E -- "Tidak" --> B
    C -- "Ya" --> G["Validasi & normalisasi data"]
    F --> G
    G --> H{"Melewati ambang bahaya?"}
    H -- "Tidak" --> Z([Selesai siklus, tunggu penarikan berikutnya])
    H -- "Ya" --> I["Digital Twin mensimulasikan area terdampak"]
    I --> J["Routing Engine menghitung ulang rute"]
    J --> K["Pecah rute ke beberapa alternatif (anti-bottleneck)"]
    K --> L["Kirim push notification + rute aman ke warga"]
    K --> M["Perbarui tampilan Digital Twin di dashboard BPBD"]
    L --> N([Selesai])
    M --> N
```

## 2. Alur Laporan Warga (SOS) dan Verifikasi

```mermaid
flowchart TD
    A([Warga menekan tombol laporan]) --> B["Pilih jenis: jalan tertutup / jalan aman"]
    B --> C["Aplikasi mengirim laporan + lokasi"]
    C --> D{"Koneksi tersedia?"}
    D -- "Tidak" --> E["Simpan di antrean lokal, kirim ulang saat online"]
    E --> C
    D -- "Ya" --> F["Server menghitung skor kepercayaan"]
    F --> G{"Skor di atas ambang?"}
    G -- "Ya" --> H["Ruas ditandai sementara, rute dihitung ulang"]
    G -- "Tidak" --> I["Masuk antrean tinjauan BPBD"]
    I --> J{"BPBD memverifikasi?"}
    J -- "Valid" --> H
    J -- "Tidak valid" --> K["Laporan ditolak, skor pelapor disesuaikan"]
    H --> L([Rute warga di sekitar diperbarui])
    K --> M([Selesai])
```

## 3. Alur Pemblokiran Rute Manual oleh BPBD

```mermaid
flowchart TD
    A([Operator login]) --> B["Pilih ruas jalan di peta"]
    B --> C{"Aksi?"}
    C -- "Blokir" --> D["Ruas ditandai tertutup (diblokir manual)"]
    C -- "Buka" --> E["Ruas dibuka kembali"]
    D --> F["Routing Engine menghitung ulang rute"]
    E --> F
    F --> G["Notifikasi pembaruan rute ke warga terdampak"]
    G --> H([Selesai])
```
