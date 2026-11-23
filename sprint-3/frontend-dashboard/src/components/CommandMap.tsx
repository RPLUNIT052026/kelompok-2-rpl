import { useEffect } from 'react'
import { AlertTriangle, Crosshair, LocateFixed, Map as MapIcon } from 'lucide-react'
import {
  CircleMarker,
  GeoJSON,
  MapContainer,
  Polyline,
  TileLayer,
  Tooltip,
  useMap,
} from 'react-leaflet'
import type { GeoJsonObject } from 'geojson'
import type {
  EvacuationResponse,
  HazardsResponse,
  HazardItem,
  RoadSegment,
  RWOption,
  RoadSegmentStatus,
} from '../types/hyperevac'

interface CommandMapProps {
  rw: RWOption
  hazards?: HazardsResponse
  routes?: EvacuationResponse
  segments: RoadSegment[]
  stale: boolean
  loading: boolean
  routeError?: string
  onSelectSegment: (segment: RoadSegment) => void
}

const hazardColors: Record<string, string> = {
  WASPADA: '#fbbf24',
  SIAGA: '#fb923c',
  AWAS: '#f87171',
}

const roadColors: Record<RoadSegmentStatus, string> = {
  AMAN: '#34d399',
  MENUNGGU_TINJAUAN: '#fbbf24',
  TERTUTUP_SEMENTARA: '#fb923c',
  TERTUTUP: '#f87171',
  TERTUTUP_MANUAL: '#ef4444',
}

function MapViewport({
  center,
}: {
  center: [number, number]
}) {
  const map = useMap()

  useEffect(() => {
    map.setView(center, 14)
  }, [center, map])

  return null
}

function hazardStyle(hazard: HazardItem) {
  const color = hazardColors[hazard.level_bahaya] ?? hazardColors.WASPADA
  return {
    color,
    fillColor: color,
    fillOpacity: hazard.level_bahaya === 'AWAS' ? 0.3 : 0.2,
    weight: 1.5,
    dashArray: '5 5',
  }
}

function roadCoordinates(segment: RoadSegment): [number, number][] {
  return segment.geometri.coordinates.map(([lng, lat]) => [lat, lng])
}

export function CommandMap({
  rw,
  hazards,
  routes,
  segments,
  stale,
  loading,
  routeError,
  onSelectSegment,
}: CommandMapProps) {
  const boundary = hazards?.rw.batas_wilayah as GeoJsonObject | undefined

  return (
    <div className="command-map relative min-h-[430px] flex-1 overflow-hidden rounded-lg border border-slate-800 bg-[#0c1421]">
      <MapContainer
        center={[rw.lat, rw.lng]}
        zoom={14}
        scrollWheelZoom
        zoomControl
        className="h-full min-h-[430px] w-full"
      >
        <MapViewport center={[rw.lat, rw.lng]} />
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          className="dark-osm-tiles"
          maxZoom={20}
        />

        {boundary && (
          <GeoJSON
            data={boundary}
            style={{
              color: '#64748b',
              fillColor: '#111827',
              fillOpacity: 0.04,
              weight: 1,
              dashArray: '3 6',
              interactive: false,
            }}
          />
        )}

        {hazards?.hazards.map((hazard) => (
          <GeoJSON
            key={hazard.id}
            data={hazard.geometri as GeoJsonObject}
            style={() => hazardStyle(hazard)}
          />
        ))}

        {hazards?.rw.titik_kumpul && (
          <CircleMarker
            center={[
              hazards.rw.titik_kumpul.coordinates[1],
              hazards.rw.titik_kumpul.coordinates[0],
            ]}
            radius={8}
            pathOptions={{
              color: '#a7f3d0',
              fillColor: '#10b981',
              fillOpacity: 0.95,
              weight: 2,
            }}
          >
            <Tooltip direction="top" offset={[0, -6]}>
              Titik kumpul aman
            </Tooltip>
          </CircleMarker>
        )}

        {segments.map((segment) => {
          const color = roadColors[segment.status] ?? '#64748b'
          const blocked =
            segment.diblokir_manual || segment.status === 'TERTUTUP_MANUAL'
          return (
            <Polyline
              key={segment.segment_id}
              positions={roadCoordinates(segment)}
              pathOptions={{
                color,
                opacity: blocked ? 0.95 : 0.82,
                weight: blocked ? 6 : 4,
                dashArray: blocked ? '7 5' : undefined,
                lineCap: 'round',
                lineJoin: 'round',
              }}
              eventHandlers={{
                click: () => onSelectSegment(segment),
                mouseover: (event) => event.target.setStyle({ weight: 7, opacity: 1 }),
                mouseout: (event) =>
                  event.target.setStyle({
                    weight: blocked ? 6 : 4,
                    opacity: blocked ? 0.95 : 0.82,
                  }),
              }}
            >
              <Tooltip sticky>
                <span className="font-mono text-[10px]">
                  {segment.segment_id.slice(0, 8).toUpperCase()}
                </span>
                <span> · {segment.status.replaceAll('_', ' ')}</span>
                <br />
                <span>Klik untuk kendali manual</span>
              </Tooltip>
            </Polyline>
          )
        })}
      </MapContainer>

      <div className="map-overlay map-title-overlay">
        <div className="flex h-8 w-8 items-center justify-center rounded-md border border-slate-700 bg-[#111827]/95">
          <MapIcon className="h-4 w-4 text-slate-300" />
        </div>
        <div>
          <p className="text-xs font-semibold text-slate-100">Peta Operasional</p>
          <p className="mt-0.5 font-mono text-[9px] tracking-wide text-slate-500">
            {hazards?.rw.nama_rw ?? rw.label} · WGS 84
          </p>
        </div>
        <span className="ml-auto flex items-center gap-1.5 rounded border border-amber-400/15 bg-[#111827]/95 px-2 py-1 text-[9px] text-amber-100/80">
          <Crosshair className="h-3 w-3 text-amber-300" />
          {hazards?.hazards.length ?? 0} ZONA
        </span>
      </div>

      <div className="map-overlay map-source-overlay">
        <span className={`h-1.5 w-1.5 rounded-full ${stale ? 'bg-amber-400' : 'bg-emerald-400'}`} />
        <span>Sumber: BMKG</span>
        {stale && <span className="text-amber-300">· CACHE</span>}
      </div>

      <div className="map-legend">
        {[
          ['AMAN', 'bg-emerald-400'],
          ['WASPADA', 'bg-amber-400'],
          ['SIAGA', 'bg-orange-400'],
          ['AWAS / TUTUP', 'bg-rose-400'],
        ].map(([label, color]) => (
          <span className="flex items-center gap-1.5" key={label}>
            <span className={`h-1.5 w-1.5 rounded-full ${color}`} />
            {label}
          </span>
        ))}
        <span className="ml-auto hidden items-center gap-1.5 sm:flex">
          <LocateFixed className="h-3 w-3 text-emerald-300" />
          Titik kumpul
        </span>
      </div>

      {routes?.evakuasi_vertikal && (
        <div className="map-alert" role="alert">
          <AlertTriangle className="h-4 w-4 shrink-0 text-rose-300" />
          <div>
            <p className="text-xs font-semibold text-rose-100">Evakuasi vertikal</p>
            <p className="mt-1 text-[10px] leading-4 text-rose-200/70">
              {routes.pesan_darurat ?? 'Tidak ada rute aman. Ikuti instruksi petugas.'}
            </p>
            {routes.alert_sar && (
              <p className="mt-1 font-mono text-[9px] uppercase tracking-wider text-rose-300">
                Alert SAR aktif
              </p>
            )}
          </div>
        </div>
      )}

      {loading && (
        <div className="absolute bottom-12 right-3 z-[500] flex items-center gap-2 rounded border border-slate-700 bg-[#111827]/95 px-2.5 py-1.5 text-[10px] text-slate-400">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-sky-400" />
          Sinkronisasi data…
        </div>
      )}

      {routeError && segments.length === 0 && (
        <div className="absolute bottom-12 left-3 right-3 z-[500] rounded-md border border-rose-400/20 bg-[#111827]/95 p-3 text-[11px] leading-5 text-rose-100 sm:left-auto sm:max-w-[300px]">
          {routeError}
        </div>
      )}
    </div>
  )
}
