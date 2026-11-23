import { AlertTriangle, CloudSun, RadioTower } from 'lucide-react'

interface StaleDataBannerProps {
  visible: boolean
  apiUnavailable: boolean
}

export function StaleDataBanner({
  visible,
  apiUnavailable,
}: StaleDataBannerProps) {
  if (!visible && !apiUnavailable) return null

  return (
    <div
      className={`flex items-center gap-3 border-b px-5 py-2.5 ${
        apiUnavailable
          ? 'border-rose-400/20 bg-rose-400/[0.07]'
          : 'border-amber-400/20 bg-amber-400/[0.06]'
      }`}
      role="status"
    >
      {apiUnavailable ? (
        <RadioTower className="h-4 w-4 shrink-0 text-rose-300" />
      ) : (
        <AlertTriangle className="h-4 w-4 shrink-0 text-amber-300" />
      )}
      <div className="min-w-0 flex-1 text-xs leading-5">
        <span className={apiUnavailable ? 'font-semibold text-rose-200' : 'font-semibold text-amber-200'}>
          {apiUnavailable ? 'Koneksi API terputus.' : 'Data sumber sedang kedaluwarsa.'}
        </span>{' '}
        <span className="text-slate-400">
          {apiUnavailable
            ? 'Metrik yang terlihat dapat berasal dari pembaruan terakhir; operasi perubahan memerlukan koneksi aktif.'
            : 'Peta menampilkan snapshot cache terakhir. Verifikasi kondisi melalui kanal lapangan.'}
        </span>
      </div>
      <div className="hidden shrink-0 items-center gap-1.5 rounded border border-slate-700/70 bg-black/10 px-2 py-1 text-[10px] text-slate-400 sm:flex">
        <CloudSun className="h-3.5 w-3.5 text-amber-300" />
        Sumber: BMKG
      </div>
    </div>
  )
}
