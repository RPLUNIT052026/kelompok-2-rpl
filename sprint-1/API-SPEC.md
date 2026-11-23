<div align="center">

![Dokumen](https://img.shields.io/badge/DOKUMEN-API_SPEC-00f0ff?style=for-the-badge&labelColor=0b1020)
![Versi](https://img.shields.io/badge/VERSI-v1_(rancangan)-7b5cff?style=for-the-badge&labelColor=0b1020)

# 🔌 Spesifikasi API

**HyperEvac System** · Rekayasa Perangkat Lunak · Universitas Samudra

</div>

<img src="../docs/assets/divider.svg" width="100%" alt=""/>

> [!NOTE]
> Dokumen ini adalah rancangan API HyperEvac, bukan API BMKG. Contoh respons menggunakan data fiktif.

## 1. Ketentuan Umum

| Item | Ketentuan |
|---|---|
| Base URL produksi | `https://api.hyperevac.local/v1` (placeholder rancangan) |
| Base URL development | `http://localhost:8000/v1` |
| Format | JSON (`Content-Type: application/json`) |
| Autentikasi warga | Token perangkat yang didaftarkan saat aktivasi aplikasi |
| Autentikasi operator | Token akses dengan peran `operator` atau `admin` |
| Waktu | ISO 8601 UTC |
| Koordinat | `lat`, `lng` dalam WGS 84 (EPSG:4326); geometri GeoJSON |
| Atribusi | Data BMKG menyertakan `sumber: "BMKG"`; klien menampilkan atribusi sumber |
| Flag data | `data_kedaluwarsa: true` menandakan payload berasal dari cache fallback |
| Enum bahaya | `AMAN`, `WASPADA`, `SIAGA`, `AWAS`; pemicu darurat adalah `>= SIAGA` |
| Enum ruas | `AMAN`, `MENUNGGU_TINJAUAN`, `TERTUTUP_SEMENTARA`, `TERTUTUP`, `TERTUTUP_MANUAL` |
| Enum laporan | `menunggu_tinjauan`, `terverifikasi_otomatis`, `diterima`, `ditolak` |

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
| 503 | Layanan tidak tersedia |

## 2. Ringkasan Endpoint

| Method | Endpoint | Peran | FR |
|---|---|---|---|
| `GET` | `/v1/hazards?rw={id}` | Warga, Operator | FR-04 |
| `GET` | `/v1/routes/evacuation?lat={lat}&lng={lng}` | Warga | FR-05, FR-09 |
| `POST` | `/v1/reports` | Warga | FR-06 |
| `POST` | `/v1/devices/register` | Warga | FR-03 |
| `GET` | `/v1/admin/reports?status=menunggu_tinjauan` | Operator | FR-07 |
| `PATCH` | `/v1/admin/reports/{id}` | Operator | FR-07 |
| `GET` | `/v1/admin/routes/segments?rw={rw_id}` | Operator | FR-07 |
| `POST` | `/v1/admin/routes/block` | Operator | FR-07 |
| `DELETE` | `/v1/admin/routes/block/{segment_id}` | Operator | FR-07 |
| `GET` | `/v1/twin/{rw_id}` | Operator | FR-08 |
| `GET` | `/v1/health` | Publik / Maintainer | FR-10 |

## 3. Detail Endpoint

### `GET /v1/hazards?rw={id}`

Daftar bahaya aktif pada RW, batas wilayah, dan titik kumpul aman.

**Respons 200**

```json
{
  "rw": {
    "id": "3f0c6b1e-0000-0000-0000-000000000001",
    "nama_rw": "RW 05 — Gampong Jawa, Langsa Kota",
    "batas_wilayah": { "type": "Polygon", "coordinates": [] },
    "titik_kumpul": { "type": "Point", "coordinates": [97.9664134, 4.4708906] }
  },
  "data_diperbarui": "2026-09-29T08:00:00Z",
  "data_kedaluwarsa": false,
  "hazards": [
    {
      "id": "a1b2c3d4-0000-0000-0000-000000000010",
      "rw_id": "3f0c6b1e-0000-0000-0000-000000000001",
      "sumber": "BMKG",
      "jenis": "cuaca_ekstrem",
      "level_bahaya": "SIAGA",
      "tingkat_bahaya": 3.5,
      "geometri": { "type": "Polygon", "coordinates": [] },
      "waktu_data": "2026-09-29T07:00:00Z",
      "terverifikasi": false
    }
  ]
}
```

`data_kedaluwarsa: true` berarti sumber data gagal diakses dan respons memakai cache terakhir.

### `GET /v1/routes/evacuation?lat={lat}&lng={lng}`

Rute aman utama dan alternatif. Jika tidak ada rute aman, API mengembalikan instruksi evakuasi vertikal dan alert SAR.

**Respons 200 — rute tersedia**

```json
{
  "asal": { "lat": 4.4683, "lng": 97.9683 },
  "dihitung_pada": "2026-09-29T08:01:10Z",
  "evakuasi_vertikal": false,
  "pesan_darurat": null,
  "alert_sar": false,
  "rute": [
    {
      "id": "R-05",
      "rw_id": "3f0c6b1e-0000-0000-0000-000000000001",
      "utama": true,
      "jarak_m": 1850,
      "estimasi_menit": 14,
      "status": "AMAN",
      "beban_persen": 62.5,
      "segmen_dilalui": [
        {
          "segment_id": "b7a6c5d4-0000-0000-0000-000000000030",
          "rw_id": "3f0c6b1e-0000-0000-0000-000000000001",
          "geometri": {
            "type": "LineString",
            "coordinates": [[97.9683, 4.4683], [97.9693, 4.4693]]
          },
          "panjang_m": 420.0,
          "kecepatan_rata_rata_mps": 1.4,
          "kapasitas_maks": 400,
          "pengguna_aktif": 250,
          "status": "AMAN",
          "diblokir_manual": false,
          "alasan": ""
        }
      ],
      "geometri": {
        "type": "LineString",
        "coordinates": [[97.9683, 4.4683], [97.9693, 4.4693]]
      }
    },
    {
      "id": "R-06",
      "rw_id": "3f0c6b1e-0000-0000-0000-000000000001",
      "utama": false,
      "jarak_m": 2300,
      "estimasi_menit": 18,
      "status": "AMAN",
      "beban_persen": 35.0,
      "geometri": {
        "type": "LineString",
        "coordinates": [[97.9683, 4.4683], [97.9673, 4.4673]]
      }
    }
  ]
}
```

**Respons 200 — tidak ada rute aman**

```json
{
  "asal": { "lat": 4.4683, "lng": 97.9683 },
  "dihitung_pada": "2026-09-29T08:01:10Z",
  "evakuasi_vertikal": true,
  "pesan_darurat": "Tidak ada rute aman. Lakukan evakuasi vertikal ke lokasi kokoh terdekat.",
  "alert_sar": true,
  "rute": []
}
```

### `POST /v1/reports`

Menerima laporan kondisi ruas dari warga. Laporan `tertutup` dengan `skor_kepercayaan >= 0.75` dapat ditandai otomatis sebagai sementara; laporan `aman` tidak pernah membuka ruas secara otomatis.

**Body**

```json
{
  "device_id": "device-01",
  "segment_id": "b7a6c5d4-0000-0000-0000-000000000030",
  "tipe": "tertutup",
  "lat": 4.4683,
  "lng": 97.9683,
  "catatan": "Genangan di Gampong Jawa",
  "dibuat_pada": "2026-09-29T08:00:00Z"
}
```

**Respons 201 — peninjauan manual**

```json
{
  "id": "c9d8e7f6-0000-0000-0000-000000000020",
  "segment_id": "b7a6c5d4-0000-0000-0000-000000000030",
  "skor_kepercayaan": 0.5,
  "status": "menunggu_tinjauan",
  "road_segment_status": "MENUNGGU_TINJAUAN",
  "rute_dihitung_ulang": false
}
```

**Respons 201 — laporan tertutup tepercaya**

```json
{
  "id": "c9d8e7f6-0000-0000-0000-000000000021",
  "segment_id": "b7a6c5d4-0000-0000-0000-000000000030",
  "skor_kepercayaan": 0.82,
  "status": "terverifikasi_otomatis",
  "road_segment_status": "TERTUTUP_SEMENTARA",
  "rute_dihitung_ulang": true
}
```

### `POST /v1/devices/register`

Mendaftarkan perangkat warga dan token push untuk FR-03.

**Body**

```json
{
  "device_id": "device-01",
  "fcm_token": "push-token-placeholder",
  "rw_id": "3f0c6b1e-0000-0000-0000-000000000001"
}
```

**Respons 201**

```json
{
  "device_id": "device-01",
  "rw_id": "3f0c6b1e-0000-0000-0000-000000000001",
  "terdaftar": true,
  "reputasi": 0.5,
  "terakhir_aktif": "2026-09-29T08:00:00Z"
}
```

### `GET /v1/admin/reports?status=menunggu_tinjauan`

Mengambil antrean laporan untuk Operator BPBD.

**Respons 200**

```json
{
  "data": [
    {
      "id": "c9d8e7f6-0000-0000-0000-000000000020",
      "segment_id": "b7a6c5d4-0000-0000-0000-000000000030",
      "device_id": "device-01",
      "tipe": "tertutup",
      "lat": 4.4683,
      "lng": 97.9683,
      "catatan": "Genangan di Gampong Jawa",
      "skor_kepercayaan": 0.5,
      "status": "menunggu_tinjauan",
      "diverifikasi_oleh": null,
      "dibuat_pada": "2026-09-29T08:00:00Z"
    }
  ]
}
```

### `PATCH /v1/admin/reports/{id}`

Operator menerima atau menolak laporan. Keputusan memperbarui status laporan dan reputasi perangkat; keputusan atas laporan tertutup juga mengubah status ruas dan memicu kalkulasi ulang bila diperlukan.

**Body**

```json
{
  "keputusan": "diterima"
}
```

`keputusan` hanya menerima `diterima` atau `ditolak`.

**Respons 200**

```json
{
  "id": "c9d8e7f6-0000-0000-0000-000000000020",
  "status": "diterima",
  "road_segment_status": "TERTUTUP",
  "reputasi_diperbarui": true,
  "rute_dihitung_ulang": true
}
```

### `POST /v1/admin/routes/block`

Operator memblokir ruas secara manual.

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
  "status": "TERTUTUP_MANUAL",
  "diblokir_manual": true,
  "rute_dihitung_ulang": true
}
```

### `DELETE /v1/admin/routes/block/{segment_id}`

Membatalkan blokir manual. **Respons 200**

```json
{
  "segment_id": "b7a6c5d4-0000-0000-0000-000000000030",
  "status": "AMAN",
  "diblokir_manual": false,
  "rute_dihitung_ulang": true
}
```

### `GET /v1/admin/routes/segments?rw={rw_id}`

Mengambil seluruh geometri dan status ruas pada satu RW untuk peta kendali operator, termasuk ruas tertutup yang tidak muncul di hasil rute aman.

**Respons 200**

```json
{
  "data": [
    {
      "segment_id": "b7a6c5d4-0000-0000-0000-000000000030",
      "rw_id": "3f0c6b1e-0000-0000-0000-000000000001",
      "geometri": {
        "type": "LineString",
        "coordinates": [[97.9683, 4.4683], [97.9703, 4.4723]]
      },
      "panjang_m": 480.0,
      "kecepatan_rata_rata_mps": 1.4,
      "kapasitas_maks": 400,
      "pengguna_aktif": 100,
      "status": "AMAN",
      "diblokir_manual": false,
      "alasan": ""
    }
  ]
}
```

### `GET /v1/twin/{rw_id}`

Mengambil snapshot Digital Twin untuk dashboard. Digital Twin 100% berbasis perangkat lunak (*software-based*), tanpa sensor fisik/IoT. Nilai `tinggi_genangan_cm` merupakan estimasi dari data curah hujan BMKG, laporan warga, atau input manual Operator BPBD; nilai tersebut bukan pembacaan sensor.

**Respons 200**

```json
{
  "id": "5b2a1c00-0000-0000-0000-000000000001",
  "rw_id": "3f0c6b1e-0000-0000-0000-000000000001",
  "zona_bahaya": { "type": "Polygon", "coordinates": [] },
  "tinggi_genangan_cm": 35.0,
  "ruas_tertutup": 2,
  "estimasi_warga_terdampak": 1420,
  "perangkat_aktif": 1420,
  "diperbarui_pada": "2026-09-29T08:01:10Z"
}
```

### `GET /v1/health`

**Respons 200**

```json
{
  "status": "ok",
  "komponen": {
    "postgres_postgis": "ok",
    "redis_cache": "ok",
    "aggregator": "ok",
    "sumber_bmkg": "ok",
    "sumber_usgs": "degraded"
  },
  "usia_cache_detik": {
    "bmkg": 30,
    "usgs": 125
  },
  "latensi_db_ms": 12,
  "versi": "0.1.0"
}
```

## 4. Catatan Perancangan

| Aspek | Keputusan |
|---|---|
| Pembatasan laju | Diterapkan di load balancer untuk melindungi backend dari lonjakan |
| Data kedaluwarsa | Ditandai eksplisit agar klien dapat menampilkan usia data |
| Privasi | Lokasi hanya dikirim saat diperlukan dan tidak disimpan lebih lama dari kebutuhan |
| Versi | Prefiks `/v1` menjaga kompatibilitas klien |
