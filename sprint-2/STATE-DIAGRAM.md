<div align="center">

![Dokumen](https://img.shields.io/badge/DOKUMEN-STATE_DIAGRAM-00f0ff?style=for-the-badge&labelColor=0b1020)
![Versi](https://img.shields.io/badge/VERSI-v1_(rancangan)-7b5cff?style=for-the-badge&labelColor=0b1020)

# ⚡ State Diagram

**HyperEvac System** · Rekayasa Perangkat Lunak · Universitas Samudra

</div>

<img src="../assets/divider.svg" width="100%" alt=""/>

## 1. Perubahan Status Ruas Jalan & Kalkulasi Rute Darurat

Diagram ini memodelkan siklus status ruas jalan dan rute evakuasi ketika menerima laporan darurat dari warga ataupun tindakan blokir manual oleh operator BPBD.

```mermaid
stateDiagram-v2
    [*] --> Aman : Inisialisasi Sistem Normal

    Aman --> MenungguTinjauan : Warga Kirim Laporan SOS (POST /v1/reports)
    MenungguTinjauan --> Aman : Laporan Ditolak / Validasi Gagal
    MenungguTinjauan --> Tertutup : Laporan Diverifikasi BPBD / Kondisi Kritis

    Aman --> TertutupManual : Operator Blokir Jalur (POST /v1/admin/routes/block)

    state TertutupManual {
        [*] --> SetStatusBlokir : diblokir_manual = true
        SetStatusBlokir --> RecalculateEngine : Panggil Routing Engine
        RecalculateEngine --> RuteDiperbarui : rute_dihitung_ulang = true
    }

    TertutupManual --> Aman : Operator Membuka Kembali Jalur (DELETE /v1/admin/routes/block/{id})
    Tertutup --> Aman : Kondisi Lapangan Pulih & Diverifikasi Operator
