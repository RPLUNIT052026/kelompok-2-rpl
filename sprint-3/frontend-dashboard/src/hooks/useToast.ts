import { createContext, useContext } from 'react'

export type ToastKind = 'success' | 'error' | 'info'

interface ToastContextValue {
  notify: (kind: ToastKind, title: string, message?: string) => void
}

export const ToastContext = createContext<ToastContextValue | null>(null)

export function useToast(): ToastContextValue {
  const context = useContext(ToastContext)
  if (!context) throw new Error('useToast must be used within ToastProvider')
  return context
}
