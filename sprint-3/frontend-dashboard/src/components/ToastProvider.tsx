import { useCallback, useEffect, useState } from 'react'
import { AlertCircle, CheckCircle2, Info, X } from 'lucide-react'
import type { ReactNode } from 'react'
import { ToastContext, type ToastKind } from '../hooks/useToast'

interface ToastItem {
  id: number
  kind: ToastKind
  title: string
  message?: string
}

let nextToastId = 0

function ToastCard({
  toast,
  dismiss,
}: {
  toast: ToastItem
  dismiss: (id: number) => void
}) {
  useEffect(() => {
    const timer = window.setTimeout(() => dismiss(toast.id), 5_000)
    return () => window.clearTimeout(timer)
  }, [dismiss, toast.id])

  const Icon =
    toast.kind === 'success'
      ? CheckCircle2
      : toast.kind === 'error'
        ? AlertCircle
        : Info
  const tone =
    toast.kind === 'success'
      ? 'text-emerald-300'
      : toast.kind === 'error'
        ? 'text-rose-300'
        : 'text-sky-300'

  return (
    <div className="toast-card" role={toast.kind === 'error' ? 'alert' : 'status'}>
      <Icon className={`mt-0.5 h-4 w-4 shrink-0 ${tone}`} aria-hidden="true" />
      <div className="min-w-0 flex-1">
        <p className="text-sm font-semibold text-slate-100">{toast.title}</p>
        {toast.message && (
          <p className="mt-1 text-xs leading-5 text-slate-400">{toast.message}</p>
        )}
      </div>
      <button
        className="icon-button -mr-1 -mt-1 h-7 w-7"
        type="button"
        aria-label="Tutup notifikasi"
        onClick={() => dismiss(toast.id)}
      >
        <X className="h-3.5 w-3.5" />
      </button>
    </div>
  )
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([])
  const dismiss = useCallback((id: number) => {
    setToasts((items) => items.filter((item) => item.id !== id))
  }, [])
  const notify = useCallback(
    (kind: ToastKind, title: string, message?: string) => {
      const id = ++nextToastId
      setToasts((items) => [...items.slice(-3), { id, kind, title, message }])
    },
    [],
  )

  return (
    <ToastContext.Provider value={{ notify }}>
      {children}
      <div className="toast-stack" aria-live="polite" aria-relevant="additions">
        {toasts.map((toast) => (
          <ToastCard key={toast.id} toast={toast} dismiss={dismiss} />
        ))}
      </div>
    </ToastContext.Provider>
  )
}
