<div align="center">

![Dokumen](https://img.shields.io/badge/DOKUMEN-UI_UX_WIREFRAME-00f0ff?style=for-the-badge&labelColor=0b1020)
![Status](https://img.shields.io/badge/STATUS-RANCANGAN-7b5cff?style=for-the-badge&labelColor=0b1020)

# 🎨 UI/UX Wireframe

**HyperEvac System** · Rekayasa Perangkat Lunak · Universitas Samudra

</div>

<img src="../docs/assets/divider.svg" width="100%" alt=""/>

<img width="906" height="89" alt="image" src="https://github.com/user-attachments/assets/10efcb4e-b6cd-42a1-badc-00331c8a633c" />
<img width="186" height="388" alt="image" src="https://github.com/user-attachments/assets/d420e96a-da10-4fa4-8935-80750db68a89" />
<img width="442" height="386" alt="image" src="https://github.com/user-attachments/assets/3e1ec2ae-9f4a-4921-b9b2-ec7acd0bbe85" />

Mobile App (Kiri): Tampilan warga saat menerima peringatan dan panduan navigasi.

Web Dashboard (Kanan): Tampilan layar sentral BPBD untuk memantau Digital Twin dan laporan warga.

## 2. Pemetaan Komponen UI ke User Story & API Endpoint

| Aplikasi / Layar | Komponen dan interaksi | User Story | Endpoint / Mekanisme |
|---|---|---|---|
| Mobile — registrasi perangkat | Registrasi `device_id`, RW, dan token push | US-03 | `POST /v1/devices/register` |
| Mobile — peta bahaya | Poligon hazard, titik kumpul aman, level bahaya dan sumber data | US-04 | `GET /v1/hazards?rw={id}` |
| Mobile — navigasi | Rute utama/alternatif, kapasitas, pengalihan, dan instruksi tanpa rute aman | US-05, US-06 | `GET /v1/routes/evacuation?lat={lat}&lng={lng}` |
| Mobile — SOS | Laporan kondisi `tertutup` atau `aman`, termasuk antrean offline | US-07 | `POST /v1/reports` |
| Mobile — peringatan | Push darurat berbasis wilayah dengan pintasan ke navigasi | US-03 | Notification Service via FCM/APNs |
| Web BPBD — dashboard wilayah | Filter RW, Digital Twin, estimasi genangan dan warga terdampak | US-09 | `GET /v1/twin/{rw_id}` |
| Web BPBD — antrean laporan | Skor kepercayaan, tipe laporan, tombol Terima/Tolak | US-08 | `GET /v1/admin/reports?status=menunggu_tinjauan`; `PATCH /v1/admin/reports/{id}` |
| Web BPBD — kendali ruas | Modal blokir/buka ruas dengan input alasan | US-08 | `POST /v1/admin/routes/block`; `DELETE /v1/admin/routes/block/{segment_id}` |
| Monitoring Console | Status PostGIS/Redis, health dan usia cache BMKG/USGS | US-10 | `GET /v1/health` |

## 3. Checklist State Antarmuka Wajib (Acuan Sprint 3)

### Mobile App Warga

- [ ] Tampilkan banner jika `data_kedaluwarsa: true` dan atribusi `Sumber: BMKG` pada data yang relevan.
- [ ] Bedakan poligon bahaya: `WASPADA` kuning, `SIAGA` oranye, dan `AWAS` merah; tampilkan titik kumpul.
- [ ] Tampilkan rute utama dan alternatif beserta status/beban, serta alert saat rute dialihkan.
- [ ] Sediakan layar fallback **Evakuasi Vertikal** ketika tidak ditemukan rute aman.
- [ ] Tampilkan indikator **Offline Queue** untuk laporan SOS yang menunggu koneksi.
- [ ] Dukung registrasi token perangkat untuk push notification.

### Web Dashboard BPBD

- [ ] Sediakan filter RW dan tampilan Live Digital Twin: `tinggi_genangan_cm`, ruas tertutup, dan `estimasi_warga_terdampak`.
- [ ] Sediakan tabel antrean laporan dengan `skor_kepercayaan` serta aksi Terima/Tolak.
- [ ] Sediakan modal blokir/buka ruas manual dengan input `alasan` dan status ruas yang jelas.
- [ ] Tampilkan penanda usia data/cache agar Operator dapat membedakan data aktual dan fallback.
