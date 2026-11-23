import { useState, type FormEvent } from 'react'
import {
  Activity,
  Check,
  ChevronDown,
  KeyRound,
  MapPinned,
  RefreshCw,
  Shield,
} from 'lucide-react'
import { getOperatorToken, saveOperatorToken } from '../api/client'
import type { HealthResponse, RWOption } from '../types/hyperevac'

interface HeaderBarProps {
  rwOptions: RWOption[]
  selectedRW: string
  health?: HealthResponse
  healthError: boolean
  refreshing: boolean
  onSelectRW: (rwId: string) => void
  onRefresh: () => void
  onTokenSaved: () => void
}

export function HeaderBar({
  rwOptions,
  selectedRW,
  health,
  healthError,
  refreshing,
  onSelectRW,
  onRefresh,
  onTokenSaved,
}: HeaderBarProps) {
  const [token, setToken] = useState(getOperatorToken)
  const [saved, setSaved] = useState(false)
  const tokenActive = Boolean(token.trim())

  function handleSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    saveOperatorToken(token)
    setToken(token.trim())
    setSaved(true)
    onTokenSaved()
    window.setTimeout(() => setSaved(false), 1_800)
  }

  const healthTone = healthError
    ? 'bg-rose-400'
    : health?.status === 'ok'
      ? 'bg-emerald-400'
      : health
        ? 'bg-amber-400'
        : 'bg-slate-600'
  const healthLabel = healthError
    ? 'API terputus'
    : health?.status === 'ok'
      ? 'Sistem online'
      : health
        ? 'Sistem terbatas'
        : 'Menghubungkan'

  return (
    <header className="relative z-[1000] flex min-h-[68px] items-center justify-between gap-3 border-b border-slate-800 bg-[#0c121e] px-4 py-2.5 shadow-panel sm:px-6">
      <div className="flex min-w-0 items-center gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-emerald-400/20 bg-emerald-400/10">
          <Shield className="h-5 w-5 text-emerald-300" strokeWidth={1.8} />
        </div>
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <p className="truncate text-[13px] font-bold tracking-[0.16em] text-slate-100">
              HYPEREVAC
            </p>
            <span className="hidden rounded border border-slate-700 px-1.5 py-0.5 font-mono text-[9px] tracking-wide text-slate-500 sm:inline">
              BPBD / COMMAND
            </span>
          </div>
          <div className="mt-1 flex items-center gap-1.5 text-[10px] uppercase tracking-[0.12em] text-slate-500">
            <span className={`h-1.5 w-1.5 rounded-full ${healthTone}`} />
            {healthLabel}
          </div>
        </div>
      </div>

      <div className="flex shrink-0 items-center gap-2 sm:gap-3">
        <label className="flex items-center gap-2 rounded-md border border-slate-800 bg-[#111827] px-2.5 py-1.5">
          <MapPinned className="hidden h-4 w-4 text-slate-500 sm:block" />
          <span className="sr-only">Pilih wilayah RW</span>
          <select
            className="max-w-[108px] cursor-pointer bg-transparent text-xs font-medium text-slate-200 outline-none sm:max-w-none"
            value={selectedRW}
            onChange={(event) => onSelectRW(event.target.value)}
            aria-label="Pilih wilayah RW"
          >
            {rwOptions.map((option) => (
              <option className="bg-[#111827]" key={option.id} value={option.id}>
                {option.label}
              </option>
            ))}
          </select>
          <ChevronDown className="h-3 w-3 text-slate-500" aria-hidden="true" />
        </label>

        <button
          className="button-secondary h-9 px-2.5 sm:px-3"
          type="button"
          onClick={onRefresh}
          disabled={refreshing}
          title="Muat ulang data dashboard"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${refreshing ? 'animate-spin' : ''}`} />
          <span className="hidden sm:inline">Refresh</span>
        </button>

        <details className="token-menu">
          <summary className="button-secondary h-9 list-none px-2.5 sm:px-3">
            <KeyRound className={`h-3.5 w-3.5 ${tokenActive ? 'text-emerald-300' : 'text-amber-300'}`} />
            <span className="hidden sm:inline">Operator</span>
            <span
              className={`h-1.5 w-1.5 rounded-full ${tokenActive ? 'bg-emerald-400' : 'bg-amber-400'}`}
              aria-label={tokenActive ? 'Token aktif' : 'Token belum diatur'}
            />
          </summary>
          <form className="token-popover" onSubmit={handleSave}>
            <div className="mb-3 flex items-start justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-slate-100">Akses operator</p>
                <p className="mt-1 text-xs leading-5 text-slate-500">
                  Token disimpan di sesi browser ini, tidak dibundel ke aplikasi.
                </p>
              </div>
              <Activity className="mt-0.5 h-4 w-4 text-slate-500" />
            </div>
            <label className="sr-only" htmlFor="operator-token">
              Bearer token operator
            </label>
            <input
              id="operator-token"
              className="input-dark w-full"
              type="password"
              autoComplete="off"
              placeholder="Tempel token operator"
              value={token}
              onChange={(event) => setToken(event.target.value)}
            />
            <div className="mt-3 flex items-center justify-between gap-2">
              <p className="text-[11px] text-slate-500">
                {tokenActive ? 'Token tersedia untuk aksi admin.' : 'Diperlukan untuk Twin & antrean.'}
              </p>
              <button className="button-primary h-8 px-3 text-xs" type="submit">
                {saved ? <Check className="h-3.5 w-3.5" /> : null}
                {saved ? 'Tersimpan' : 'Simpan'}
              </button>
            </div>
          </form>
        </details>

        <div className="hidden items-center gap-2 border-l border-slate-800 pl-3 lg:flex">
          <span className={`h-2 w-2 rounded-full ${healthTone}`} />
          <span className="font-mono text-[10px] tracking-wide text-slate-500">
            {health?.versi ? `API v${health.versi}` : 'API v—'}
          </span>
        </div>
      </div>
    </header>
  )
}
