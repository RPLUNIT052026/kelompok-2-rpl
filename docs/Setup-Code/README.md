# ⚙️ HyperEvac System — Setup Code & Prototipe (Siklus 1)

Folder ini berisi kode sumber untuk **Siklus 1 (MVP Core: API Engine)** dari **HyperEvac System**. Pada siklus ini, sistem fokus pada penarikan data real-time dari API publik BMKG, parsing data, evaluasi tingkat bahaya, mitigasi kegagalan jaringan (retry + fallback cache), serta penyediaan infrastruktur database spasial berbasis **PostgreSQL + PostGIS**.

---

## 📁 Struktur Direktori

```text
setup-code/
├── README.md               # Dokumentasi panduan eksekusi (file ini)
├── requirements.txt        # Dependensi Python
├── .env.example            # Template variabel lingkungan
├── docker-compose.yml      # Service Container Database PostGIS
└── aggregator/
    ├── __init__.py         # Inisialisasi paket Python
    ├── fetch_bmkg.py       # Script utama penarik & parser data BMKG
    ├── conftest.py         # Konfigurasi pengujian & sys.path
    └── test_parse.py       # Unit test parser & fallback cache (offline)
```

---

## 🛠️ Persyaratan Sistem

Sebelum menjalankan prototipe, pastikan perangkat Anda telah terinstal:
* **Python** `>= 3.10`
* **Docker** & **Docker Compose** (opsional, jika ingin menguji database PostGIS lokal)
* **Git**

---

## 🚀 Langkah Instalasi & Penggunaan

### 1. Salin Konfigurasi Environment
Salin file `.env.example` menjadi `.env`:
```bash
cp .env.example .env
```

### 2. Install Dependensi Python
Sangat disarankan menggunakan virtual environment (`venv`):
```bash
# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Install library pendukung
pip install -r requirements.txt
```

---

## 🗄️ Menjalankan Database PostGIS (Opsional)

Untuk menjalankan instance PostgreSQL dengan ekstensi PostGIS secara cepat menggunakan Docker:

```bash
# Menyalakan container database
docker-compose up -d

# Memeriksa status container
docker-compose ps
```

Sistem database akan berjalan di `localhost:5432` dengan kredensial default yang ada di `.env.example`. File SQL skema lengkap dapat dilihat di [`../Desain-dan-Arsitektur/CLASS-DAN-DATABASE.md`](../Desain-dan-Arsitektur/CLASS-DAN-DATABASE.md).

---

## 🐍 Menjalankan Agregator Data BMKG

Script `aggregator/fetch_bmkg.py` dapat dijalankan langsung via perintah CLI.

### A. Menampilkan Output Tabel (Tampilan Terminal)
```bash
python aggregator/fetch_bmkg.py --adm4 31.71.03.1001
```

### B. Menampilkan Output Format JSON (Guna Integrasi API/Backend)
```bash
python aggregator/fetch_bmkg.py --adm4 31.71.03.1001 --json
```

### C. Opsi / Flag CLI yang Tersedia
```bash
python aggregator/fetch_bmkg.py --help
```
* `--adm4`: Kode wilayah administrasi tingkat IV (Kelurahan/Desa) untuk prakiraan cuaca.
* `--json`: Mengubah format keluaran menjadi objek JSON murni.
* `--skip-gempa`: Melewati pengambilan data gempa.
* `--skip-cuaca`: Melewati pengambilan data prakiraan cuaca.
* `--cache-dir`: Menentukan direktori penyimpanan cache lokal (default: `.cache`).
* `-v, --verbose`: Menampilkan log debug secara terperinci.

---

## 🧪 Menjalankan Unit Testing

Proyek ini dilengkapi dengan unit test tanpa membutuhkan koneksi jaringan aktif (*offline mock testing*) untuk memastikan *parser* dan mekanisme *fallback cache* berfungsi handal.

### Menggunakan `pytest` (Rekomendasi)
Jalankan perintah ini dari dalam folder `setup-code/`:
```bash
pytest
```

### Menggunakan Module `unittest` Bawaan Python
```bash
python -m unittest discover -s aggregator
```

---

## 🔒 Ketentuan Penggunaan Data BMKG

Sesuai dengan ketentuan BMKG (Badan Meteorologi, Klimatologi, dan Geofisika), seluruh penggunaan data pada modul ini menyertakan atribusi resmi:
> *Sumber data: BMKG (Badan Meteorologi, Klimatologi, dan Geofisika)*
