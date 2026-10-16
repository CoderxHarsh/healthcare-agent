import { useEffect, useRef, type ReactNode } from 'react'
import { Link } from 'react-router-dom'
import {
  AlertTriangle,
  CheckCircle2,
  Info,
  MinusCircle,
  XCircle,
  type LucideIcon,
} from 'lucide-react'
import { APP_NAME, APP_TAGLINE } from '../config'
import type { RangeStatus } from '../lib/metrics'

/** Rounded teal square with a medical cross whose horizontal arm carries a small pulse line. */
export function BrandMark({ size = 40 }: { size?: number }) {
  return (
    <span className="brand-mark" style={{ width: size, height: size }} aria-hidden="true">
      <svg width={size * 0.6} height={size * 0.6} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M9 3h6v6h6v6h-6v6H9v-6H3V9h6z" />
        <path d="M5.5 12h3l1.5-2.5 2 5 1.5-2.5h4" strokeWidth="1.5" />
      </svg>
    </span>
  )
}

export function Brand() {
  return (
    <Link to="/" className="brand" aria-label={`${APP_NAME} home`}>
      <BrandMark />
      <span className="brand-text">
        <div className="brand-name">{APP_NAME}</div>
        <div className="brand-sub">{APP_TAGLINE}</div>
      </span>
    </Link>
  )
}

export type Tone = 'success' | 'warning' | 'error' | 'info'

const NOTICE_ICONS: Record<Tone, LucideIcon> = {
  success: CheckCircle2,
  warning: AlertTriangle,
  error: XCircle,
  info: Info,
}

export function ToneIcon({ tone, size = 18 }: { tone: Tone; size?: number }) {
  const Icon = NOTICE_ICONS[tone]
  return <Icon className="icon" size={size} aria-hidden="true" />
}

/** Inline message: always an icon plus text so meaning never relies on colour alone. */
export function Notice({ tone, children }: { tone: Tone; children: ReactNode }) {
  return (
    <div className={`notice notice-${tone}`} role={tone === 'error' ? 'alert' : undefined}>
      <ToneIcon tone={tone} />
      <div>{children}</div>
    </div>
  )
}

const STATUS: Record<RangeStatus, { cls: string; label: string; Icon: LucideIcon }> = {
  in: { cls: 'chip-ok', label: 'In range', Icon: CheckCircle2 },
  out: { cls: 'chip-warn', label: 'Outside range', Icon: AlertTriangle },
  unknown: { cls: 'chip-muted', label: 'No reference', Icon: MinusCircle },
}

export function StatusChip({ status }: { status: RangeStatus }) {
  const { cls, label, Icon } = STATUS[status]
  return (
    <span className={`chip ${cls}`}>
      <Icon className="icon" size={14} aria-hidden="true" />
      {label}
    </span>
  )
}

export function StatusIcon({ status, size = 16 }: { status: RangeStatus; size?: number }) {
  const { Icon, label } = STATUS[status]
  const color = status === 'in' ? 'var(--success)' : status === 'out' ? 'var(--warning)' : 'var(--muted)'
  return <Icon className="icon" size={size} color={color} aria-label={label} role="img" />
}

interface ConfirmProps {
  title: string
  children: ReactNode
  confirmLabel: string
  busy?: boolean
  onConfirm: () => void
  onCancel: () => void
}

/** Modal confirmation: focus moves into the dialog, Escape cancels, and focus returns on close. */
export function ConfirmDialog({ title, children, confirmLabel, busy, onConfirm, onCancel }: ConfirmProps) {
  const cancelRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null
    cancelRef.current?.focus()
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onCancel()
    }
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('keydown', onKey)
      previous?.focus()
    }
  }, [onCancel])

  return (
    <div className="dialog-backdrop" onClick={onCancel}>
      <div
        className="dialog"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id="dialog-title">{title}</h2>
        <div>{children}</div>
        <div className="dialog-actions">
          <button ref={cancelRef} type="button" className="btn btn-secondary" onClick={onCancel} disabled={busy}>
            Cancel
          </button>
          <button type="button" className="btn btn-danger" onClick={onConfirm} disabled={busy}>
            {busy ? 'Working...' : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}
