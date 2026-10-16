import { createContext, useCallback, useContext, useRef, useState, type ReactNode } from 'react'

type ToastKind = 'success' | 'warning' | 'error' | 'info'

interface Toast {
  id: number
  kind: ToastKind
  text: string
}

type Notify = (kind: ToastKind, text: string) => void

const ToastContext = createContext<Notify | null>(null)

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])
  const nextId = useRef(1)

  const notify = useCallback<Notify>((kind, text) => {
    const id = nextId.current++
    setToasts((current) => [...current, { id, kind, text }])
    setTimeout(() => setToasts((current) => current.filter((t) => t.id !== id)), 5000)
  }, [])

  return (
    <ToastContext.Provider value={notify}>
      {children}
      <div className="toasts" role="status" aria-live="polite">
        {toasts.map((t) => (
          <div key={t.id} className={`toast toast-${t.kind}`}>
            {t.text}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast(): Notify {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used inside <ToastProvider>')
  return ctx
}

export function errorMessage(err: unknown): string {
  return err instanceof Error ? err.message : String(err)
}
