export type HazardLevel = 'AMAN' | 'WASPADA' | 'SIAGA' | 'AWAS'

export type RoadSegmentStatus =
  | 'AMAN'
  | 'MENUNGGU_TINJAUAN'
  | 'TERTUTUP_SEMENTARA'
  | 'TERTUTUP'
  | 'TERTUTUP_MANUAL'

export type ReportType = 'tertutup' | 'aman'

export type ReportStatus =
  | 'menunggu_tinjauan'
  | 'terverifikasi_otomatis'
  | 'diterima'
  | 'ditolak'

export interface PointGeometry {
  type: 'Point'
  coordinates: [number, number]
}

export interface LineStringGeometry {
  type: 'LineString'
  coordinates: [number, number][]
}

export interface PolygonGeometry {
  type: 'Polygon'
  coordinates: [number, number][][]
}

export interface MultiPolygonGeometry {
  type: 'MultiPolygon'
  coordinates: [number, number][][][]
}

export type GeoJSONGeometry =
  | PointGeometry
  | LineStringGeometry
  | PolygonGeometry
  | MultiPolygonGeometry

export interface RWInfo {
  id: string
  nama_rw: string
  batas_wilayah: PolygonGeometry
  titik_kumpul: PointGeometry
}

export interface HazardItem {
  id: string
  rw_id: string
  sumber: string
  jenis: string
  level_bahaya: HazardLevel
  tingkat_bahaya: number
  geometri: PolygonGeometry | MultiPolygonGeometry
  waktu_data: string
  terverifikasi: boolean
}

export interface HazardsResponse {
  rw: RWInfo
  data_diperbarui: string
  data_kedaluwarsa: boolean
  hazards: HazardItem[]
}

export interface DigitalTwin {
  id: string
  rw_id: string
  zona_bahaya: PolygonGeometry | MultiPolygonGeometry | null
  tinggi_genangan_cm: number
  ruas_tertutup: number
  estimasi_warga_terdampak: number
  perangkat_aktif: number
  diperbarui_pada: string
}

export interface RoadSegment {
  segment_id: string
  rw_id: string
  geometri: LineStringGeometry
  panjang_m: number
  kecepatan_rata_rata_mps: number
  kapasitas_maks: number
  pengguna_aktif: number
  status: RoadSegmentStatus
  diblokir_manual: boolean
  alasan: string
}

export interface RoadSegmentListResponse {
  data: RoadSegment[]
}

export interface EvacuationRoute {
  id: string
  rw_id: string
  utama: boolean
  jarak_m: number
  estimasi_menit: number
  status: RoadSegmentStatus
  beban_persen: number
  segmen_dilalui: RoadSegment[]
  geometri: LineStringGeometry
}

export interface EvacuationResponse {
  asal: { lat: number; lng: number }
  dihitung_pada: string
  evakuasi_vertikal: boolean
  pesan_darurat: string | null
  alert_sar: boolean
  rute: EvacuationRoute[]
}

export interface ReportItem {
  id: string
  segment_id: string
  device_id: string
  tipe: ReportType
  lat: number
  lng: number
  catatan: string
  skor_kepercayaan: number
  status: ReportStatus
  diverifikasi_oleh: string | null
  dibuat_pada: string
}

export interface ReportQueueResponse {
  data: ReportItem[]
}

export interface ReportDecisionResponse {
  id: string
  status: ReportStatus
  road_segment_status: RoadSegmentStatus
  reputasi_diperbarui: boolean
  rute_dihitung_ulang: boolean
}

export interface ManualBlockResponse {
  segment_id: string
  status: RoadSegmentStatus
  diblokir_manual: boolean
  rute_dihitung_ulang: boolean
}

export interface HealthResponse {
  status: string
  komponen: {
    postgres_postgis: string
    redis_cache: string
    aggregator: string
    sumber_bmkg: string
    sumber_usgs: string
  }
  usia_cache_detik: { bmkg: number; usgs: number }
  latensi_db_ms: number
  versi: string
}

export interface RWOption {
  id: string
  label: string
  lat: number
  lng: number
}
