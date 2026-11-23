import {
  Activity,
  Clock3,
  Droplets,
  Radio,
  Route,
  UsersRound,
} from 'lucide-react'
import type { DigitalTwin } from '../types/hyperevac'

interface DigitalTwinStatsProps {
  twin?: DigitalTwin
  loading: boolean
  error?: string
}

function formatUpdatedAt(value?: string): string {
  if (!value) return '—'
  const date = new Date(value)
  return Number.isNaN(date.getTime())
    ? '—'
    : new Intl.DateTimeFormat('id-ID', {
        hour: '2-digit',
        minute: '2-digit',
        day: '2-digit',
        month: 'short',
      }).format(date)
}

export function DigitalTwinStats({ twin, loading, error }: DigitalTwinStatsProps) {
  const metrics = [
    {
      label: 'Estimasi genangan',
      value: twin ? twin.tinggi_genangan_cm.toLocaleString('id-ID') : '—',
      unit: 'cm',
      icon: Droplets,
      tone: 'text-sky-300',
      iconBg: 'bg-sky-400/10',
    },
    {
      label: 'Ruas tertutup',
      value: twin ? twin.ruas_tertutup.toLocaleString('id-ID') : '—',
      unit: 'ruas',
      icon: Route,
      tone: twin && twin.ruas_tertutup > 0 ? 'text-rose-300' : 'text-emerald-300',
      iconBg: twin && twin.ruas_tertutup > 0 ? 'bg-rose-400/10' : 'bg-emerald-400/10',
    },
    {
      label: 'Warga terdampak',
      value: twin ? twin.estimasi_warga_terdampak.toLocaleString('id-ID') : '—',
      unit: 'jiwa',
      icon: UsersRound,
      tone: 'text-amber-300',
      iconBg: 'bg-amber-400/10',
    },
    {
      label: 'Perangkat aktif',
      value: twin ? twin.perangkat_aktif.toLocaleString('id-ID') : '—',
      unit: 'perangkat',
      icon: Radio,
      tone: 'text-violet-300',
      iconBg: 'bg-violet-400/10',
    },
  ]

  return (
    <section className="panel-card p-4 sm:p-5" aria-labelledby="twin-heading">
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <div className="section-eyebrow">
            <Activity className="h-3.5 w-3.5 text-emerald-300" />
            LIVE SNAPSHOT
          </div>
          <h2 id="twin-heading" className="mt-1.5 text-[15px] font-semibold text-slate-100">
            Digital Twin Wilayah
          </h2>
        </div>
        <div className="flex items-center gap-1.5 rounded border border-slate-800 bg-slate-950/40 px-2 py-1 text-[10px] text-slate-500">
          <Clock3 className="h-3 w-3" />
          {formatUpdatedAt(twin?.diperbarui_pada)}
        </div>
      </div>

      {error && !twin && (
        <div className="mb-3 rounded-md border border-rose-400/15 bg-rose-400/[0.05] px-3 py-2 text-xs leading-5 text-rose-200">
          {error}
        </div>
      )}

      <div className="grid grid-cols-2 gap-2.5">
        {metrics.map((metric) => {
          const Icon = metric.icon
          return (
            <div className="metric-tile" key={metric.label}>
              <div className="flex items-center justify-between gap-2">
                <p className="text-[10px] font-medium uppercase tracking-[0.1em] text-slate-500">
                  {metric.label}
                </p>
                <span className={`flex h-7 w-7 items-center justify-center rounded-md ${metric.iconBg}`}>
                  <Icon className={`h-3.5 w-3.5 ${metric.tone}`} />
                </span>
              </div>
              <div className="mt-2 flex items-baseline gap-1.5">
                <span className={`font-mono text-[25px] font-medium leading-none tracking-tight ${metric.tone} ${loading && !twin ? 'animate-pulse' : ''}`}>
                  {metric.value}
                </span>
                <span className="text-[10px] text-slate-500">{metric.unit}</span>
              </div>
            </div>
          )
        })}
      </div>

      <div className="mt-3 rounded-md border border-sky-400/10 bg-sky-400/[0.035] px-3 py-2.5">
        <p className="text-[11px] font-medium leading-[1.65] text-sky-100/80">
          Estimasi berbasis data BMKG &amp; laporan lapangan (tanpa sensor IoT)
        </p>
        <p className="mt-1 text-[10px] text-slate-500">
          Sumber: BMKG · laporan warga · pembaruan Operator BPBD
        </p>
      </div>
    </section>
  )
}
