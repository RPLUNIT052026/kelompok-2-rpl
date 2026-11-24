import { useMemo, useState } from 'react'
import { KeyRound } from 'lucide-react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  fetchHealth,
  getApiErrorMessage,
  getOperatorToken,
  isUnauthorizedError,
} from '../api/client'
import { RW_OPTIONS, getRWOption } from '../config/rwOptions'
import { CommandMap } from '../components/CommandMap'
import { DigitalTwinStats } from '../components/DigitalTwinStats'
import { HeaderBar } from '../components/HeaderBar'
import { ManualBlockModal } from '../components/ManualBlockModal'
import { ReportQueueTable } from '../components/ReportQueueTable'
import { StaleDataBanner } from '../components/StaleDataBanner'
import { useAdminReports } from '../hooks/useAdminReports'
import { useDigitalTwin } from '../hooks/useDigitalTwin'
import { useRoadSegmentCache } from '../hooks/useRoadSegmentCache'
import { useRoadSegments } from '../hooks/useRoadSegments'
import { useRouteBlock } from '../hooks/useRouteBlock'
import { useToast } from '../hooks/useToast'
import type { ReportItem, RoadSegment } from '../types/hyperevac'

export function DashboardPage() {
  const [selectedRW, setSelectedRW] = useState(RW_OPTIONS[0].id)
  const [selectedSegment, setSelectedSegment] = useState<RoadSegment | null>(null)
  const [refreshing, setRefreshing] = useState(false)
  const rw = getRWOption(selectedRW)
  const queryClient = useQueryClient()
  const { notify } = useToast()
  const { hazards, twin, routes } = useDigitalTwin(rw)
  const roadSegments = useRoadSegments(rw.id)
  const { reports, decision } = useAdminReports()
  const { block, unblock } = useRouteBlock(rw.id)
  const health = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: 30_000,
    retry: 1,
  })

  const liveSegments = useMemo(
    () =>
      roadSegments.data?.data ??
      routes.data?.rute.flatMap((route) => route.segmen_dilalui) ??
      [],
    [roadSegments.data, routes.data],
  )
  const { segments, updateManualStatus } = useRoadSegmentCache(rw.id, liveSegments)
  const stale =
    hazards.data?.data_kedaluwarsa === true ||
    (hazards.isError && hazards.data !== undefined)
  const apiUnavailable = health.isError && health.data === undefined
  const authRequired =
    !getOperatorToken() ||
    isUnauthorizedError(twin.error) ||
    isUnauthorizedError(reports.error) ||
    isUnauthorizedError(roadSegments.error)
  const liveConnection = health.data?.status === 'ok' && !stale

  async function refreshDashboard() {
    setRefreshing(true)
    const results = await Promise.all([
      health.refetch(),
      hazards.refetch(),
      twin.refetch(),
      routes.refetch(),
      roadSegments.refetch(),
      reports.refetch(),
    ])
    const failed = results.some((result) => result.isError)
    setRefreshing(false)
    if (failed) {
      notify('error', 'Pembaruan belum lengkap', 'Sebagian endpoint API tidak merespons. Periksa koneksi dan token operator.')
    } else {
      notify('success', 'Dashboard diperbarui', 'Status wilayah, peta, dan antrean laporan telah dimuat ulang.')
    }
  }

  async function refreshAfterTokenChange() {
    await queryClient.invalidateQueries()
  }

  async function handleDecision(report: ReportItem, decisionValue: 'diterima' | 'ditolak') {
    try {
      const result = await decision.mutateAsync({
        id: report.id,
        keputusan: decisionValue,
      })
      const verb = decisionValue === 'diterima' ? 'diterima' : 'ditolak'
      notify(
        'success',
        `Laporan ${verb}`,
        result.rute_dihitung_ulang
          ? 'Rute dan Digital Twin wilayah diperbarui.'
          : 'Status laporan dan reputasi perangkat diperbarui.',
      )
    } catch (error) {
      notify('error', 'Keputusan gagal dikirim', getApiErrorMessage(error))
    }
  }

  async function handleBlock(segmentId: string, reason: string) {
    try {
      const result = await block.mutateAsync({ segmentId, alasan: reason })
      updateManualStatus(result, reason)
      setSelectedSegment(null)
      notify(
        'success',
        'Ruas berhasil diblokir',
        result.rute_dihitung_ulang
          ? 'Rute evakuasi dan Digital Twin telah dihitung ulang.'
          : 'Status blokir manual telah disimpan.',
      )
    } catch (error) {
      notify('error', 'Blokir ruas gagal', getApiErrorMessage(error))
    }
  }

  async function handleUnblock(segmentId: string) {
    try {
      const result = await unblock.mutateAsync(segmentId)
      updateManualStatus(result)
      setSelectedSegment(null)
      notify(
        'success',
        'Blokir ruas dibuka',
        result.rute_dihitung_ulang
          ? 'Status ruas kembali AMAN dan rute dihitung ulang.'
          : 'Perubahan status telah disimpan.',
      )
    } catch (error) {
      notify('error', 'Membuka blokir gagal', getApiErrorMessage(error))
    }
  }

  return (
    <div className="command-shell">
      <HeaderBar
        rwOptions={RW_OPTIONS}
        selectedRW={selectedRW}
        health={health.data}
        healthError={health.isError && health.data === undefined}
        refreshing={refreshing}
        onSelectRW={setSelectedRW}
        onRefresh={() => void refreshDashboard()}
        onTokenSaved={() => void refreshAfterTokenChange()}
      />

      <StaleDataBanner visible={stale} apiUnavailable={apiUnavailable} />

      <main className="dashboard-grid">
        <section className="map-column" aria-labelledby="map-heading">
          <div className="map-heading">
            <div>
              <div className="section-eyebrow">
                <span className="h-px w-4 bg-emerald-400" />
                PUSAT KENDALI TAKTIS
              </div>
              <h1 id="map-heading" className="mt-1 text-[19px] font-semibold tracking-tight text-slate-100">
                Situational Map
              </h1>
              <p className="mt-1 text-xs text-slate-500">
                Pantau zona bahaya, kondisi ruas, dan titik kumpul aman secara langsung.
              </p>
            </div>
            <div className="hidden items-center gap-2 rounded-md border border-slate-800 bg-[#111827]/70 px-3 py-2 sm:flex">
              <span className={`h-2 w-2 rounded-full ${liveConnection ? 'animate-pulse bg-emerald-400' : 'bg-amber-400'}`} />
              <span className={`font-mono text-[10px] tracking-wide ${liveConnection ? 'text-slate-400' : 'text-amber-200'}`}>
                {rw.label.toUpperCase()} / {liveConnection ? 'LIVE' : 'DATA TERBATAS'}
              </span>
            </div>
          </div>

          <CommandMap
            rw={rw}
            hazards={hazards.data}
            routes={routes.data}
            segments={segments}
            stale={stale || apiUnavailable}
            loading={hazards.isFetching || routes.isFetching || roadSegments.isFetching}
            routeError={
              roadSegments.error && routes.error
                ? getApiErrorMessage(roadSegments.error)
                : undefined
            }
            onSelectSegment={setSelectedSegment}
          />
          <div className="map-footer">
            <span>
              <span className="font-mono text-slate-400">{segments.length}</span> ruas pada tampilan
            </span>
            <span className="hidden sm:inline">Klik garis ruas untuk blokir atau buka manual</span>
            {hazards.data?.data_diperbarui && (
              <span className="font-mono">
                DATA {new Date(hazards.data.data_diperbarui).toLocaleTimeString('id-ID', {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>
            )}
          </div>
        </section>

        <aside className="right-panel" aria-label="Metrik Digital Twin dan antrean laporan">
          {authRequired && (
            <div className="rounded-lg border border-amber-400/20 bg-amber-400/[0.05] p-3.5">
              <div className="flex items-start gap-2.5">
                <KeyRound className="mt-0.5 h-4 w-4 shrink-0 text-amber-300" />
                <div>
                  <p className="text-xs font-semibold text-amber-100">Token operator diperlukan</p>
                  <p className="mt-1 text-[11px] leading-5 text-amber-100/60">
                    Masukkan Bearer token melalui tombol Operator di header untuk memuat Digital Twin dan memproses laporan.
                  </p>
                </div>
              </div>
            </div>
          )}

          <DigitalTwinStats
            twin={twin.data}
            loading={twin.isLoading}
            error={twin.error ? getApiErrorMessage(twin.error) : undefined}
          />

          <ReportQueueTable
            reports={reports.data?.data ?? []}
            loading={reports.isLoading}
            error={reports.error ? getApiErrorMessage(reports.error) : undefined}
            busyId={decision.isPending ? decision.variables?.id : undefined}
            onDecision={(report, value) => void handleDecision(report, value)}
          />

          <div className="flex items-center justify-between px-1 pb-1 text-[9px] uppercase tracking-[0.12em] text-slate-600">
            <span>HyperEvac · BPBD</span>
            <span className="font-mono">OPERATOR CONSOLE</span>
          </div>
        </aside>
      </main>

      {selectedSegment && (
        <ManualBlockModal
          segment={selectedSegment}
          busy={block.isPending || unblock.isPending}
          onClose={() => setSelectedSegment(null)}
          onBlock={handleBlock}
          onUnblock={handleUnblock}
        />
      )}
    </div>
  )
}
