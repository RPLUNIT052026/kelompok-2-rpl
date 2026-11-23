import { useEffect, useState, type FormEvent } from 'react'
import { AlertTriangle, ArrowUpRight, LoaderCircle, LockKeyhole, Unlock } from 'lucide-react'
import type { RoadSegment } from '../types/hyperevac'

interface ManualBlockModalProps {
  segment: RoadSegment
  busy: boolean
  onClose: () => void
  onBlock: (segmentId: string, reason: string) => Promise<void>
  onUnblock: (segmentId: string) => Promise<void>
}

function isManualBlock(segment: RoadSegment): boolean {
  return segment.diblokir_manual || segment.status === 'TERTUTUP_MANUAL'
}

export function ManualBlockModal({
  segment,
  busy,
  onClose,
  onBlock,
  onUnblock,
}: ManualBlockModalProps) {
  const [reason, setReason] = useState(segment.alasan)
  const [confirmed, setConfirmed] = useState(false)
  const isBlocked = isManualBlock(segment)

  useEffect(() => {
    function handleEscape(event: KeyboardEvent) {
      if (event.key === 'Escape' && !busy) onClose()
    }
    window.addEventListener('keydown', handleEscape)
    return () => window.removeEventListener('keydown', handleEscape)
  }, [busy, onClose])

  function submitBlock(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const trimmedReason = reason.trim()
    if (!trimmedReason) return
    void onBlock(segment.segment_id, trimmedReason)
  }

  return (
    <div
      className="modal-backdrop"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget && !busy) onClose()
      }}
    >
      <section
        aria-labelledby="manual-block-title"
        aria-modal="true"
        className="modal-panel"
        role="dialog"
      >
        <div className="flex items-start justify-between gap-4 border-b border-slate-800 px-5 py-4">
          <div className="flex items-start gap-3">
            <div className={`flex h-9 w-9 items-center justify-center rounded-lg ${isBlocked ? 'bg-rose-400/10' : 'bg-amber-400/10'}`}>
              {isBlocked ? (
                <LockKeyhole className="h-4 w-4 text-rose-300" />
              ) : (
                <AlertTriangle className="h-4 w-4 text-amber-300" />
              )}
            </div>
            <div>
              <p className="section-eyebrow">KENDALI RUAS MANUAL</p>
              <h2 id="manual-block-title" className="mt-1 text-base font-semibold text-slate-100">
                {isBlocked ? 'Buka blokir ruas' : 'Blokir ruas'}
              </h2>
            </div>
          </div>
          <button
            className="icon-button h-8 w-8"
            type="button"
            aria-label="Tutup dialog"
            disabled={busy}
            onClick={onClose}
          >
            ×
          </button>
        </div>

        <div className="space-y-4 px-5 py-4">
          <div className="rounded-md border border-slate-800 bg-slate-950/45 p-3">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-mono text-xs font-medium text-slate-200">
                  RUAS {segment.segment_id.slice(0, 8).toUpperCase()}
                </p>
                <p className="mt-1 text-[11px] text-slate-500">
                  RW · panjang {Math.round(segment.panjang_m).toLocaleString('id-ID')} m
                </p>
              </div>
              <span className={`status-pill status-${segment.status.toLowerCase()}`}>
                {segment.status.replaceAll('_', ' ')}
              </span>
            </div>
            {isBlocked && segment.alasan && (
              <p className="mt-3 border-t border-slate-800 pt-2.5 text-xs leading-5 text-slate-400">
                Alasan blokir: <span className="text-slate-300">{segment.alasan}</span>
              </p>
            )}
          </div>

          {isBlocked ? (
            <div className="space-y-3">
              <div className="flex gap-2 rounded-md border border-amber-400/15 bg-amber-400/[0.05] p-3 text-xs leading-5 text-amber-100/80">
                <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-300" />
                Membuka ruas akan mengubah status menjadi AMAN. Pastikan laporan lapangan menyatakan ruas dapat dilalui.
              </div>
              <label className="flex cursor-pointer items-start gap-2.5 text-xs leading-5 text-slate-400">
                <input
                  className="mt-1 accent-emerald-400"
                  type="checkbox"
                  checked={confirmed}
                  onChange={(event) => setConfirmed(event.target.checked)}
                />
                Saya mengonfirmasi ruas ini siap dibuka kembali.
              </label>
              <button
                className="button-primary w-full"
                type="button"
                disabled={!confirmed || busy}
                onClick={() => void onUnblock(segment.segment_id)}
              >
                {busy ? (
                  <LoaderCircle className="h-4 w-4 animate-spin" />
                ) : (
                  <Unlock className="h-4 w-4" />
                )}
                {busy ? 'Memperbarui status…' : 'Konfirmasi buka ruas'}
              </button>
            </div>
          ) : (
            <form className="space-y-3" onSubmit={submitBlock}>
              <label className="block text-xs font-medium text-slate-300" htmlFor="block-reason">
                Alasan blokir <span className="text-rose-300">*</span>
              </label>
              <textarea
                id="block-reason"
                className="input-dark min-h-[92px] w-full resize-y"
                required
                minLength={1}
                maxLength={1000}
                placeholder="Contoh: genangan tinggi di sisi utara ruas"
                value={reason}
                onChange={(event) => setReason(event.target.value)}
              />
              <div className="flex items-start gap-2 text-[10px] leading-4 text-slate-500">
                <ArrowUpRight className="mt-0.5 h-3 w-3 shrink-0" />
                Blokir manual langsung mengeluarkan ruas dari kalkulasi rute evakuasi.
              </div>
              <button
                className="button-danger w-full"
                type="submit"
                disabled={busy || reason.trim().length === 0}
              >
                {busy ? (
                  <LoaderCircle className="h-4 w-4 animate-spin" />
                ) : (
                  <LockKeyhole className="h-4 w-4" />
                )}
                {busy ? 'Mengirim blokir…' : 'Blokir ruas sekarang'}
              </button>
            </form>
          )}
        </div>
      </section>
    </div>
  )
}
