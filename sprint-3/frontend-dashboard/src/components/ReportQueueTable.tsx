import { Check, CircleAlert, LoaderCircle, X } from 'lucide-react'
import type { ReportItem } from '../types/hyperevac'

interface ReportQueueTableProps {
  reports: ReportItem[]
  loading: boolean
  error?: string
  busyId?: string
  onDecision: (report: ReportItem, decision: 'diterima' | 'ditolak') => void
}

function formatTime(value: string): string {
  const date = new Date(value)
  return Number.isNaN(date.getTime())
    ? 'Waktu tidak valid'
    : new Intl.DateTimeFormat('id-ID', {
        day: '2-digit',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit',
      }).format(date)
}

export function ReportQueueTable({
  reports,
  loading,
  error,
  busyId,
  onDecision,
}: ReportQueueTableProps) {
  return (
    <section className="panel-card overflow-hidden" aria-labelledby="reports-heading">
      <div className="flex items-center justify-between gap-3 border-b border-slate-800 px-4 py-4 sm:px-5">
        <div>
          <div className="section-eyebrow">
            <CircleAlert className="h-3.5 w-3.5 text-amber-300" />
            OPERASI LAPANGAN
          </div>
          <h2 id="reports-heading" className="mt-1.5 text-[15px] font-semibold text-slate-100">
            Antrean Laporan
          </h2>
        </div>
        <span className="flex h-6 min-w-6 items-center justify-center rounded-full border border-amber-400/20 bg-amber-400/10 px-2 font-mono text-[11px] text-amber-200">
          {loading && reports.length === 0 ? '…' : reports.length}
        </span>
      </div>

      {error && (
        <div className="mx-4 mt-3 rounded-md border border-rose-400/15 bg-rose-400/[0.05] px-3 py-2 text-xs leading-5 text-rose-200 sm:mx-5">
          {error}
        </div>
      )}

      {loading && reports.length === 0 ? (
        <div className="space-y-3 p-5" aria-label="Memuat antrean laporan">
          {[0, 1, 2].map((item) => (
            <div className="h-[88px] animate-pulse rounded-md bg-slate-800/60" key={item} />
          ))}
        </div>
      ) : reports.length === 0 ? (
        <div className="flex min-h-[160px] flex-col items-center justify-center px-6 text-center">
          <div className="flex h-10 w-10 items-center justify-center rounded-full border border-emerald-400/15 bg-emerald-400/[0.06]">
            <Check className="h-4 w-4 text-emerald-300" />
          </div>
          <p className="mt-3 text-sm font-medium text-slate-300">Antrean terkendali</p>
          <p className="mt-1 max-w-[240px] text-xs leading-5 text-slate-500">
            Tidak ada laporan warga yang menunggu verifikasi.
          </p>
        </div>
      ) : (
        <div className="max-h-[calc(100vh-420px)] min-h-[170px] overflow-auto">
          <table className="w-full border-collapse text-left">
            <thead className="sticky top-0 z-[1] bg-[#111827]">
              <tr className="border-b border-slate-800 text-[9px] uppercase tracking-[0.13em] text-slate-500">
                <th className="px-4 py-2.5 font-medium sm:px-5">Laporan / Ruas</th>
                <th className="px-2 py-2.5 font-medium">Skor</th>
                <th className="px-4 py-2.5 text-right font-medium sm:px-5">Keputusan</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/70">
              {reports.map((report) => {
                const isBusy = busyId === report.id
                const trusted = report.skor_kepercayaan >= 0.75
                return (
                  <tr className="align-top" key={report.id}>
                    <td className="max-w-[180px] px-4 py-3.5 sm:max-w-none sm:px-5">
                      <div className="flex items-center gap-2">
                        <span
                          className={`h-1.5 w-1.5 rounded-full ${
                            report.tipe === 'tertutup' ? 'bg-rose-400' : 'bg-emerald-400'
                          }`}
                        />
                        <span
                          className={`text-[10px] font-semibold uppercase tracking-wide ${
                            report.tipe === 'tertutup' ? 'text-rose-200' : 'text-emerald-200'
                          }`}
                        >
                          {report.tipe === 'tertutup' ? 'Ruas tertutup' : 'Ruas aman'}
                        </span>
                      </div>
                      <p className="mt-1.5 truncate text-xs leading-5 text-slate-300" title={report.catatan}>
                        {report.catatan || 'Tidak ada catatan lapangan'}
                      </p>
                      <p className="mt-1 font-mono text-[9px] text-slate-600">
                        {report.segment_id.slice(0, 8)} · {formatTime(report.dibuat_pada)}
                      </p>
                    </td>
                    <td className="whitespace-nowrap px-2 py-3.5">
                      <span className={`font-mono text-xs font-semibold ${trusted ? 'text-emerald-300' : 'text-amber-300'}`}>
                        {report.skor_kepercayaan.toFixed(2)}
                      </span>
                      <p className={`mt-1 text-[9px] ${trusted ? 'text-emerald-500/80' : 'text-amber-500/80'}`}>
                        {trusted ? 'tinggi' : 'perlu tinjau'}
                      </p>
                    </td>
                    <td className="whitespace-nowrap px-4 py-3.5 text-right sm:px-5">
                      <div className="flex justify-end gap-1.5">
                        <button
                          className="button-approve h-8 w-8"
                          type="button"
                          title="Terima laporan"
                          aria-label={`Terima laporan ${report.id}`}
                          disabled={isBusy}
                          onClick={() => onDecision(report, 'diterima')}
                        >
                          {isBusy ? (
                            <LoaderCircle className="h-3.5 w-3.5 animate-spin" />
                          ) : (
                            <Check className="h-3.5 w-3.5" />
                          )}
                        </button>
                        <button
                          className="button-reject h-8 w-8"
                          type="button"
                          title="Tolak laporan"
                          aria-label={`Tolak laporan ${report.id}`}
                          disabled={isBusy}
                          onClick={() => onDecision(report, 'ditolak')}
                        >
                          {isBusy ? (
                            <LoaderCircle className="h-3.5 w-3.5 animate-spin" />
                          ) : (
                            <X className="h-3.5 w-3.5" />
                          )}
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
      <div className="flex items-center justify-between border-t border-slate-800 px-4 py-2.5 text-[10px] text-slate-600 sm:px-5">
        <span>Skor ≥ 0,75 · kepercayaan tinggi</span>
        <span>Auto refresh 20 dtk</span>
      </div>
    </section>
  )
}
