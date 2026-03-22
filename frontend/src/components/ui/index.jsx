import React, { useEffect, useRef } from 'react'
import clsx from 'clsx'

// ── Button ────────────────────────────────────────────────────────────────────
export function Button({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  icon: Icon,
  className,
  disabled,
  ...props
}) {
  const variants = {
    primary:   'btn-primary',
    secondary: 'btn-secondary',
    danger:    'btn-danger',
    ghost:     'bg-transparent hover:bg-surface-muted text-text-secondary hover:text-text-primary border border-transparent hover:border-surface-border font-medium rounded-lg transition-all duration-200',
  }
  const sizes = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2.5 text-sm',
    lg: 'px-5 py-3 text-base',
  }

  return (
    <button
      className={clsx(variants[variant], sizes[size], 'inline-flex items-center gap-2', className)}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? <Spinner size="sm" /> : Icon && <Icon size={14} />}
      {children}
    </button>
  )
}

// ── Input ─────────────────────────────────────────────────────────────────────
export function Input({ label, error, icon: Icon, className, ...props }) {
  return (
    <div className="w-full">
      {label && <label className="label">{label}</label>}
      <div className="relative">
        {Icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted">
            <Icon size={15} />
          </div>
        )}
        <input
          className={clsx('input', Icon && 'pl-9', error && 'border-red-500 focus:ring-red-500', className)}
          {...props}
        />
      </div>
      {error && <p className="mt-1 text-xs text-red-400">{error}</p>}
    </div>
  )
}

// ── Select ────────────────────────────────────────────────────────────────────
export function Select({ label, error, children, className, ...props }) {
  return (
    <div className="w-full">
      {label && <label className="label">{label}</label>}
      <select
        className={clsx(
          'input appearance-none',
          error && 'border-red-500 focus:ring-red-500',
          className
        )}
        {...props}
      >
        {children}
      </select>
      {error && <p className="mt-1 text-xs text-red-400">{error}</p>}
    </div>
  )
}

// ── Textarea ──────────────────────────────────────────────────────────────────
export function Textarea({ label, error, className, rows = 3, ...props }) {
  return (
    <div className="w-full">
      {label && <label className="label">{label}</label>}
      <textarea
        rows={rows}
        className={clsx('input resize-none', error && 'border-red-500 focus:ring-red-500', className)}
        {...props}
      />
      {error && <p className="mt-1 text-xs text-red-400">{error}</p>}
    </div>
  )
}

// ── Spinner ───────────────────────────────────────────────────────────────────
export function Spinner({ size = 'md', className }) {
  const sizes = { sm: 'w-4 h-4', md: 'w-6 h-6', lg: 'w-10 h-10' }
  return (
    <svg
      className={clsx('animate-spin text-brand-500', sizes[size], className)}
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  )
}

// ── PageLoader ────────────────────────────────────────────────────────────────
export function PageLoader({ text = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center h-64 gap-4">
      <Spinner size="lg" />
      <p className="text-text-muted text-sm">{text}</p>
    </div>
  )
}

// ── Skeleton ──────────────────────────────────────────────────────────────────
export function Skeleton({ className }) {
  return (
    <div className={clsx('bg-surface-border rounded-lg animate-pulse', className)} />
  )
}

export function SkeletonCard() {
  return (
    <div className="card space-y-3">
      <Skeleton className="h-4 w-1/3" />
      <Skeleton className="h-8 w-1/2" />
      <Skeleton className="h-3 w-2/3" />
    </div>
  )
}

export function SkeletonTable({ rows = 5 }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton key={i} className="h-12 w-full" />
      ))}
    </div>
  )
}

// ── EmptyState ────────────────────────────────────────────────────────────────
export function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center px-4">
      {Icon && (
        <div className="w-16 h-16 rounded-2xl bg-surface-border flex items-center justify-center mb-5">
          <Icon size={28} className="text-text-muted" />
        </div>
      )}
      <h3 className="text-base font-semibold text-text-primary mb-1">{title}</h3>
      {description && <p className="text-sm text-text-secondary max-w-xs mb-5">{description}</p>}
      {action}
    </div>
  )
}

// ── Modal ─────────────────────────────────────────────────────────────────────
export function Modal({ open, onClose, title, children, size = 'md' }) {
  const overlayRef = useRef(null)
  useEffect(() => {
    const handleKey = (e) => { if (e.key === 'Escape') onClose?.() }
    if (open) {
      document.addEventListener('keydown', handleKey)
      document.body.style.overflow = 'hidden'
    }
    return () => {
      document.removeEventListener('keydown', handleKey)
      document.body.style.overflow = ''
    }
  }, [open, onClose])

  if (!open) return null

  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
  }

  return (
    <div ref={overlayRef} className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className={clsx('relative w-full bg-surface-card border border-surface-border rounded-2xl shadow-card animate-slide-up', sizes[size])}>
        <div className="flex items-center justify-between px-6 py-4 border-b border-surface-border">
          <h2 className="text-base font-semibold text-text-primary">{title}</h2>
          <button onClick={onClose} className="p-1.5 rounded-lg text-text-muted hover:text-text-primary hover:bg-surface-border transition-colors">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="px-6 py-5 overflow-y-auto max-h-[70vh]
          [&::-webkit-scrollbar]:w-1
          [&::-webkit-scrollbar-track]:bg-transparent
          [&::-webkit-scrollbar-thumb]:bg-surface-border
          [&::-webkit-scrollbar-thumb]:rounded-full
          hover:[&::-webkit-scrollbar-thumb]:bg-surface-border/80">
          {children}
        </div>
      </div>
    </div>
  )
}

// ── ConfirmDialog ─────────────────────────────────────────────────────────────
export function ConfirmDialog({ open, onClose, onConfirm, title, message, confirmLabel = 'Confirm', loading = false }) {
  return (
    <Modal open={open} onClose={onClose} title={title} size="sm">
      <p className="text-sm text-text-secondary mb-6">{message}</p>
      <div className="flex justify-end gap-3">
        <Button variant="secondary" onClick={onClose} disabled={loading}>Cancel</Button>
        <Button variant="danger" onClick={onConfirm} loading={loading}>{confirmLabel}</Button>
      </div>
    </Modal>
  )
}

// ── Rating Badge ──────────────────────────────────────────────────────────────
export function RatingBadge({ rating }) {
  if (!rating) return <span className="text-text-muted text-xs">—</span>
  const classes = {
    outstanding:       'badge-outstanding',
    good:              'badge-good',
    satisfactory:      'badge-satisfactory',
    needs_improvement: 'badge-needs_improvement',
    poor:              'badge-poor',
  }
  const labels = {
    outstanding:       'Outstanding',
    good:              'Good',
    satisfactory:      'Satisfactory',
    needs_improvement: 'Needs Improvement',
    poor:              'Poor',
  }
  return <span className={classes[rating] || 'badge-inactive'}>{labels[rating] || rating}</span>
}

// ── Status Badge ──────────────────────────────────────────────────────────────
export function StatusBadge({ status, active }) {
  const key = (status || (active ? 'active' : 'inactive')).toLowerCase()

  const styles = {
    // assignment statuses
    active:     { background: 'rgba(34,197,94,0.1)',   color: '#4ade80', border: '1px solid rgba(34,197,94,0.2)'   },
    inactive:   { background: 'rgba(100,116,139,0.1)', color: '#94a3b8', border: '1px solid rgba(100,116,139,0.2)' },
    completed:  { background: 'rgba(59,130,246,0.1)',  color: '#60a5fa', border: '1px solid rgba(59,130,246,0.2)'  },
    // approval statuses
    pending:    { background: 'rgba(249,115,22,0.1)',  color: '#fb923c', border: '1px solid rgba(249,115,22,0.2)'  },
    approved:   { background: 'rgba(34,197,94,0.1)',   color: '#4ade80', border: '1px solid rgba(34,197,94,0.2)'   },
    rejected:   { background: 'rgba(239,68,68,0.1)',   color: '#f87171', border: '1px solid rgba(239,68,68,0.2)'   },
    // summary types
    individual: { background: 'rgba(129,140,248,0.1)', color: '#818cf8', border: '1px solid rgba(129,140,248,0.2)' },
    team:       { background: 'rgba(52,211,153,0.1)',  color: '#34d399', border: '1px solid rgba(52,211,153,0.2)'  },
    department: { background: 'rgba(251,146,60,0.1)',  color: '#fb923c', border: '1px solid rgba(251,146,60,0.2)'  },
  }

  const style = styles[key] || styles.inactive

  return (
    <span style={{
      ...style,
      display: 'inline-block',
      padding: '2px 10px',
      borderRadius: '9999px',
      fontSize: '0.75rem',
      fontWeight: 500,
      textTransform: 'capitalize',
    }}>
      {key}
    </span>
  )
}

// ── Stat Card ─────────────────────────────────────────────────────────────────
export function StatCard({ title, value, subtitle, icon: Icon, color = 'brand', trend, loading }) {
  const colors = {
    brand:  { bg: 'bg-brand-500/10',   icon: 'text-brand-400',   border: 'border-brand-500/20' },
    green:  { bg: 'bg-emerald-500/10', icon: 'text-emerald-400', border: 'border-emerald-500/20' },
    amber:  { bg: 'bg-amber-500/10',   icon: 'text-amber-400',   border: 'border-amber-500/20' },
    red:    { bg: 'bg-red-500/10',     icon: 'text-red-400',     border: 'border-red-500/20' },
    blue:   { bg: 'bg-blue-500/10',    icon: 'text-blue-400',    border: 'border-blue-500/20' },
  }
  const c = colors[color] || colors.brand

  if (loading) return <SkeletonCard />

  return (
    <div className="card flex items-start gap-4 animate-fade-in">
      <div className={clsx('p-3 rounded-xl border', c.bg, c.border)}>
        {Icon && <Icon size={20} className={c.icon} />}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-xs font-medium text-text-muted uppercase tracking-wide">{title}</p>
        <p className="text-2xl font-bold text-text-primary mt-0.5">{value ?? '—'}</p>
        {subtitle && <p className="text-xs text-text-secondary mt-0.5">{subtitle}</p>}
        {trend !== undefined && (
          <p className={clsx('text-xs mt-1 font-medium', trend >= 0 ? 'text-emerald-400' : 'text-red-400')}>
            {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}%
          </p>
        )}
      </div>
    </div>
  )
}

// ── Table ─────────────────────────────────────────────────────────────────────
export function Table({ headers, children, loading, rows = 5 }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-surface-border">
      <table className="w-full">
        <thead className="bg-surface-muted">
          <tr>
            {headers.map((h) => (
              <th key={h} className="table-header text-left">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-surface-border">
          {loading ? (
            Array.from({ length: rows }).map((_, i) => (
              <tr key={i}>
                {headers.map((h) => (
                  <td key={h} className="table-cell">
                    <Skeleton className="h-4 w-3/4" />
                  </td>
                ))}
              </tr>
            ))
          ) : children}
        </tbody>
      </table>
    </div>
  )
}

// ── Page Header ───────────────────────────────────────────────────────────────
export function PageHeader({ title, subtitle, actions }) {
  return (
    <div className="flex items-start justify-between mb-6 gap-4 flex-wrap">
      <div>
        <h1 className="page-title">{title}</h1>
        {subtitle && <p className="page-subtitle">{subtitle}</p>}
      </div>
      {actions && <div className="flex items-center gap-3 flex-wrap">{actions}</div>}
    </div>
  )
}

// ── Error Message ─────────────────────────────────────────────────────────────
export function ErrorMessage({ message, onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="w-14 h-14 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center mb-4">
        <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <p className="text-sm text-text-secondary mb-4">{message || 'Something went wrong'}</p>
      {onRetry && (
        <Button variant="secondary" size="sm" onClick={onRetry}>Try again</Button>
      )}
    </div>
  )
}

// ── Data Table ────────────────────────────────────────────────────────────────
export function DataTable({ columns, data = [], loading, emptyTitle, emptyDescription, emptyAction }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-surface-border">
      <table className="w-full">
        <thead className="bg-surface-muted">
          <tr>
            {columns.map((col) => (
              <th key={col.header} className="table-header text-left">{col.header}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-surface-border">
          {loading && Array.from({ length: 5 }).map((_, i) => (
            <tr key={i}>
              {columns.map((col) => (
                <td key={col.header} className="table-cell">
                  <Skeleton className="h-4 w-3/4" />
                </td>
              ))}
            </tr>
          ))}
          {!loading && data.length === 0 && (
            <tr>
              <td colSpan={columns.length}>
                <EmptyState
                  title={emptyTitle || 'No data yet'}
                  description={emptyDescription}
                  action={emptyAction}
                />
              </td>
            </tr>
          )}
          {!loading && data.map((row, i) => (
            <tr key={row.uuid || i} className="table-row">
              {columns.map((col) => (
                <td key={col.header} className="table-cell">
                  {col.render
                    ? col.render(row)
                    : <span className="text-text-secondary">{row[col.key] ?? '—'}</span>
                  }
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ── Detail Row ────────────────────────────────────────────────────────────────
export function DetailRow({ label, value }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-text-secondary">{label}</span>
      <span className="text-sm text-text-primary font-medium">{value}</span>
    </div>
  )
}

// ── Score Badge ───────────────────────────────────────────────────────────────
export function ScoreBadge({ score }) {
  const s = parseFloat(score)
  if (isNaN(s)) return <span className="text-text-muted">—</span>
  const color = s >= 90 ? '#4ade80' : s >= 75 ? '#818cf8' : s >= 60 ? '#fb923c' : '#f87171'
  return <span style={{ color }} className="font-bold text-sm">{s.toFixed(1)}%</span>
}

// ── Score Bar ─────────────────────────────────────────────────────────────────
export function ScoreBar({ score }) {
  const s     = Math.min(parseFloat(score) || 0, 100)
  const color = s >= 90 ? '#4ade80' : s >= 75 ? '#818cf8' : s >= 60 ? '#fb923c' : '#f87171'
  return (
    <div className="w-20 h-1.5 bg-surface-border rounded-full overflow-hidden">
      <div style={{ width: `${s}%`, backgroundColor: color }} className="h-full rounded-full" />
    </div>
  )
}