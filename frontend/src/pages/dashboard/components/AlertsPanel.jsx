import React, { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { alertsApi } from '../../../api'
import { Button, Modal } from '../../../components/ui'
import toast from 'react-hot-toast'

// ── Alert type config
const ALERT_CONFIG = {
  underperformance:       { color: '#f87171', bg: 'rgba(239,68,68,0.1)',    label: 'Underperformance'     },
  excellent:              { color: '#4ade80', bg: 'rgba(34,197,94,0.1)',    label: 'Excellent'            },
  'Average performance':  { color: '#fb923c', bg: 'rgba(251,146,60,0.1)',  label: 'Average Performance'  },
  'Improved performance': { color: '#818cf8', bg: 'rgba(129,140,248,0.1)', label: 'Improved Performance' },
}

// ── Resolve modal — uses reusable Modal component
function ResolveModal({ alert, onClose, onConfirm, loading }) {
  const [note, setNote] = useState('')
  return (
    <Modal open={!!alert} onClose={onClose} title="Resolve Alert" size="sm">
      {/* Alert info */}
      <div className="bg-surface-muted rounded-lg p-3 space-y-1">
        <p className="text-text-primary text-sm font-medium">{alert.kpi_name}</p>
        <p className="text-text-muted text-xs">{alert.message}</p>
      </div>

      {/* Resolution note */}
      <div>
        <label className="label">Resolution Note (optional)</label>
        <textarea
          className="input min-h-[80px] resize-none"
          placeholder="Describe the action taken e.g. Coached employee, adjusted target..."
          value={note}
          onChange={e => setNote(e.target.value)}
        />
      </div>

      {/* Actions — uses reusable Button */}
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="secondary" onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button onClick={() => onConfirm(alert.id, note)} loading={loading}>
          Mark Resolved
        </Button>
      </div>
    </Modal>
  )
}

export default function AlertsPanel({ alerts = [], onResolved }) {
  const queryClient     = useQueryClient()
  const [expanded,      setExpanded]      = useState(false)
  const [resolveTarget, setResolveTarget] = useState(null)
  const [filter,        setFilter]        = useState('unresolved')

  const unresolved = alerts.filter(a => !a.is_resolved)
  const resolved   = alerts.filter(a =>  a.is_resolved)
  const filtered   = filter === 'unresolved' ? unresolved
                   : filter === 'resolved'   ? resolved
                   : alerts

  const resolveMutation = useMutation({
    mutationFn: ({ id, note }) => alertsApi.resolve(id, { resolution_note: note }),
    onSuccess: () => {
      toast.success('Alert resolved')
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      setResolveTarget(null)
      if (onResolved) onResolved()
    },
    onError: (err) => toast.error(err.response?.data?.message || 'Failed to resolve'),
  })

  const resolveAllMutation = useMutation({
    mutationFn: () => alertsApi.resolveAll(),
    onSuccess: () => {
      toast.success('All alerts resolved')
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      if (onResolved) onResolved()
    },
    onError: () => toast.error('Failed to resolve all alerts'),
  })

  if (alerts.length === 0) return null

  return (
    <div className="bg-[#1a1d27] border border-white/10 rounded-2xl overflow-hidden">

      {/* ── Header */}
      <div
        className="flex items-center justify-between px-5 py-4 cursor-pointer hover:bg-white/[0.02] transition-colors"
        onClick={() => setExpanded(p => !p)}
      >
        <div className="flex items-center gap-3">
          <span className="text-lg">🔔</span>
          <div>
            <h2 className="text-white font-semibold text-sm">KPI Alerts</h2>
            <p className="text-slate-500 text-xs mt-0.5">
              {unresolved.length} unresolved · {resolved.length} resolved
            </p>
          </div>
          {unresolved.length > 0 && (
            <span className="bg-amber-500/20 text-amber-400 text-xs font-bold px-2 py-0.5 rounded-full border border-amber-500/30">
              {unresolved.length}
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          {/* Resolve All — uses reusable Button */}
          {unresolved.length > 0 && expanded && (
            <Button
              variant="secondary"
              size="sm"
              onClick={(e) => { e.stopPropagation(); resolveAllMutation.mutate() }}
              loading={resolveAllMutation.isPending}
            >
              Resolve All
            </Button>
          )}
          <svg
            width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"
            className={`text-slate-400 transition-transform ${expanded ? 'rotate-180' : ''}`}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      {/* ── Expanded content */}
      {expanded && (
        <div className="border-t border-white/10">

          {/* Filter tabs */}
          <div className="flex items-center gap-1 px-5 py-3 border-b border-white/5">
            {[
              { key: 'unresolved', label: 'Unresolved', count: unresolved.length },
              { key: 'resolved',   label: 'Resolved',   count: resolved.length   },
              { key: 'all',        label: 'All',         count: alerts.length     },
            ].map(f => (
              <button
                key={f.key}
                onClick={() => setFilter(f.key)}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                  filter === f.key
                    ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                    : 'text-slate-500 hover:text-slate-300 hover:bg-white/5'
                }`}
              >
                {f.label} ({f.count})
              </button>
            ))}
          </div>

          {/* Alert list */}
          <div className="max-h-80 overflow-y-auto divide-y divide-white/5
            [&::-webkit-scrollbar]:w-1
            [&::-webkit-scrollbar-track]:bg-transparent
            [&::-webkit-scrollbar-thumb]:bg-white/10
            [&::-webkit-scrollbar-thumb]:rounded-full">

            {filtered.length === 0 ? (
              <div className="px-5 py-8 text-center">
                <p className="text-slate-600 text-sm">
                  {filter === 'unresolved' ? 'All alerts resolved ✓' : 'No alerts found'}
                </p>
              </div>
            ) : filtered.map(alert => {
              const cfg = ALERT_CONFIG[alert.alert_type] || ALERT_CONFIG.excellent
              return (
                <div key={alert.id} className="flex items-start gap-4 px-5 py-3.5">

                  {/* Type badge */}
                  <span
                    style={{ color: cfg.color, background: cfg.bg }}
                    className="text-xs font-medium px-2 py-0.5 rounded-full flex-shrink-0 mt-0.5"
                  >
                    {cfg.label}
                  </span>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <p className="text-white text-sm font-medium">{alert.kpi_name}</p>
                    <p className="text-slate-500 text-xs mt-0.5 truncate">{alert.message}</p>
                    {alert.is_resolved && alert.resolution_note && (
                      <p className="text-slate-600 text-xs mt-1 italic">
                        Note: {alert.resolution_note}
                      </p>
                    )}
                    {alert.is_resolved && alert.resolved_by && (
                      <p className="text-slate-600 text-xs">
                        Resolved by {alert.resolved_by} · {alert.resolved_at}
                      </p>
                    )}
                  </div>

                  {/* Score */}
                  {alert.threshold && (
                    <span className="text-xs text-slate-400 flex-shrink-0">
                      {alert.threshold}%
                    </span>
                  )}

                  {/* Resolve button — uses reusable Button */}
                  {!alert.is_resolved ? (
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => setResolveTarget(alert)}
                    >
                      Resolve
                    </Button>
                  ) : (
                    <span className="flex-shrink-0 text-xs text-emerald-500">✓</span>
                  )}

                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* ── Resolve Modal */}
      {resolveTarget && (
        <ResolveModal
          alert={resolveTarget}
          onClose={() => setResolveTarget(null)}
          onConfirm={(id, note) => resolveMutation.mutate({ id, note })}
          loading={resolveMutation.isPending}
        />
      )}

    </div>
  )
}