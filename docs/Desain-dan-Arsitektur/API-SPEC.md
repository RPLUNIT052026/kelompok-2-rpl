<div align="center">

![Dokumen](https://img.shields.io/badge/DOKUMEN-API_SPEC-00f0ff?style=for-the-badge&labelColor=0b1020)
![Versi](https://img.shields.io/badge/VERSI-v1_(rancangan)-7b5cff?style=for-the-badge&labelColor=0b1020)

# 🔌 Spesifikasi API

**HyperEvac System** · Rekayasa Perangkat Lunak · Universitas Samudra

</div>

<img src="../docs/assets/divider.svg" width="100%" alt=""/>

> [!NOTE]
> Spesifikasi ini adalah **rancangan** endpoint HyperEvac (bukan API BMKG). Contoh respons berisi data fiktif. Daftar endpoint mengacu ke [`docs/PROPOSAL.md`](../docs/PROPOSAL.md).

## 1. Ketentuan Umum

| Item | Ketentuan |
|---|---|
| Base URL | `https://<domain-hyperevac>/v1` |
| Format | JSON (`Content-Type: application/json`) |
| Autentikasi warga | Token perangkat (didaftarkan saat pertama membuka aplikasi) |
| Autentikasi operator | Token akses + peran (`operator`, `admin`) |
| Waktu | ISO 8601, zona UTC |
| Koordinat | `lat`, `lng` dalam WGS 84 (EPSG:4326) |
| Atribusi | Respons yang memuat data BMKG menyertakan `sumber: "BMKG"`; aplikasi wajib menampilkan BMKG sebagai sumber data |

### Format Error

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Parameter lat dan lng wajib diisi",
    "details": []
  }
}
```

| HTTP | Arti |
|---|---|
| 400 | Parameter tidak valid |
| 401 | Belum terautentikasi |
| 403 | Peran tidak diizinkan |
| 404 | Data tidak ditemukan |
| 429 | Terlalu banyak permintaan |
| 503 | Layanan sedang tidak tersedia |

## 2. Ringkasan Endpoint

| Method | Endpoint | Peran | FR |
|---|---|---|---|
| `GET` | `/v1/hazards?rw={id}` | Warga, Operator | FR-01, FR-04 |
| `GET` | `/v1/routes/evacuation?lat=&lng=` | Warga | FR-05, FR-09 |
| `POST` | `/v1/reports` | Warga | FR-06 |
| `POST` | `/v1/admin/routes/block` | Operator | FR-07 |
| `DELETE` | `/v1/admin/routes/block/{id}` | Operator | FR-07 |
| `GET` | `/v1/twin/{rw_id}` | Operator | FR-08 |
| `GET` | `/v1/health` | Publik / Maintainer | FR-10 |

## 3. Detail Endpoint

### `GET /v1/hazards?rw={id}`

Daftar bahaya aktif pada suatu RW.

**Respons 200**

```json
{
  "rw": { "id": "3f0c6b1e-0000-0000-0000-000000000001", "nama": "RW 05" },
  "data_diperbarui": "2026-09-29T08:00:00Z",
  "data_kedaluwarsa": false,
  "hazards": [
    {
      "id": "a1b2c3d4-0000-0000-0000-000000000010",
      "sumber": "BMKG",
      "jenis": "cuaca_ekstrem",
      "tingkat_bahaya": 3.5,
      "waktu_data": "2026-09-29T07:00:00Z",
      "terverifikasi": false
    }
  ]
}
```

`data_kedaluwarsa: true` berarti API sumber sedang gagal dan sistem memakai cache terakhir.

### `GET /v1/routes/evacuation?lat={lat}&lng={lng}`

Rute evakuasi teraman dari posisi warga, beserta alternatif.

**Respons 200**

```json
{
  "asal": { "lat": -6.1, "lng": 106.8 },
  "dihitung_pada": "2026-09-29T08:01:10Z",
  "rute": [
    {
      "id": "R-05",
      "utama": true,
      "jarak_m": 1850,
      "estimasi_menit": 14,
      "status": "aman",
      "geometri": {
        "type": "LineString",
        "coordinates": [[106.8, -6.1], [106.801, -6.099]]
      }
    },
    {
      "id": "R-06",
      "utama": false,
      "jarak_m": 2300,
      "estimasi_menit": 18,
      "status": "aman",
      "geometri": { "type": "LineString", "coordinates": [[106.8, -6.1], [106.799, -6.101]] }
    }
  ]
}
```

### `POST /v1/reports`

Warga melaporkan kondisi jalan.

**Body**

```json
{
  "tipe": "tertutup",
  "lat": -6.1,
  "lng": 106.8,
  "catatan": "Jembatan tergenang setinggi lutut"
}
```

**Respons 201**

```json
{
  "id": "c9d8e7f6-0000-0000-0000-000000000020",
  "skor_kepercayaan": 0.5,
  "status": "menunggu_tinjauan"
}
```

### `POST /v1/admin/routes/block`

Operator memblokir ruas jalan secara manual.

**Body**

```json
{
  "segment_id": "b7a6c5d4-0000-0000-0000-000000000030",
  "alasan": "Longsor di ruas jalan"
}
```

**Respons 200**

```json
{
  "segment_id": "b7a6c5d4-0000-0000-0000-000000000030",
  "status": "tertutup",
  "diblokir_manual": true,
  "rute_dihitung_ulang": true
}
```

### `DELETE /v1/admin/routes/block/{id}`

Membuka kembali ruas yang diblokir manual. **Respons 204** tanpa body.

### `GET /v1/twin/{rw_id}`

Status Digital Twin untuk dashboard.

**Respons 200**

```json
{
  "rw_id": "3f0c6b1e-0000-0000-0000-000000000001",
  "zona_bahaya": { "type": "Polygon", "coordinates": [] },
  "ruas_tertutup": 2,
  "perangkat_aktif": 1420,
  "latensi_ms": 120
}
```

### `GET /v1/health`

**Respons 200**

```json
{
  "status": "ok",
  "komponen": {
    "database": "ok",
    "aggregator": "ok",
    "sumber_bmkg": "degraded"
  },
  "versi": "0.1.0"
}
```

## 4. Catatan Perancangan

| Aspek | Keputusan |
|---|---|
| Pembatasan laju | Diterapkan di load balancer untuk melindungi backend dari lonjakan |
| Data kedaluwarsa | Selalu ditandai eksplisit agar aplikasi bisa menampilkan peringatan usia data |
| Privasi | Lokasi hanya dikirim saat diperlukan; tidak disimpan lebih lama dari kebutuhan simulasi |
| Versi | Prefiks `/v1` agar perubahan di siklus berikutnya tidak merusak klien lama |
