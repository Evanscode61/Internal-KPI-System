import React from 'react'
import { DataTable, RatingBadge, StatusBadge } from '../../components/ui'
import { Eye, Pencil, Check, Trash2 } from 'lucide-react'

export default function KpiResultsTable({
  results, loading,
  isEmployee, isManager, isAdminOrHR,
  canDelete,
  onView, onEdit, onResubmit, onReview, onDelete,
}) {
  const columns = [
    {
      header: 'KPI Name',
      render: (r) => <span className="text-text-primary font-medium">{r.kpi_name}</span>,
    },
    ...(!isEmployee ? [{
      header: 'Employee',
      render: (r) => <span className="text-text-secondary">{r.submitted_by || '—'}</span>,
    }] : []),
    ...(!isEmployee ? [{
      header: 'Department',
      render: (r) => <span className="text-text-secondary">{r.department || '—'}</span>,
    }] : []),
    {
      header: 'Target',
      render: (r) => (
        <span className="text-text-secondary">
          {r.target ?? '—'}
          <span className="text-text-muted text-xs ml-1">{r.measurement_type || ''}</span>
        </span>
      ),
    },
    {
      header: 'Actual',
      render: (r) => (
        <span className="text-text-primary font-semibold">
          {parseFloat(r.actual_value).toFixed(1)}
          <span className="text-text-muted text-xs ml-1">{r.measurement_type || ''}</span>
        </span>
      ),
    },
    {
      header: 'Score',
      render: (r) => (
        <span className="text-text-primary font-semibold">
          {r.calculated_score ? `${parseFloat(r.calculated_score).toFixed(1)}%` : '—'}
        </span>
      ),
    },
    {
      header: 'Rating',
      render: (r) => <RatingBadge rating={r.rating} />,
    },
    {
      header: 'Approval',
      render: (r) => <StatusBadge status={r.approval_status} />,
    },
    {
      header: 'Period',
      render: (r) => (
        <span className="text-text-muted text-xs whitespace-nowrap">
          {r.period_start || '—'} → {r.period_end || '—'}
        </span>
      ),
    },
    {
      header: 'Actions',
      render: (r) => (
        <div className="flex items-center gap-1">
          <button onClick={() => onView(r)} className="p-1.5 rounded-lg text-text-muted hover:text-brand-400 hover:bg-brand-500/10 transition-colors" title="View details">
            <Eye size={14} />
          </button>
          {isEmployee && r.approval_status === 'pending' && (
            <button onClick={() => onEdit(r)} className="p-1.5 rounded-lg text-text-muted hover:text-amber-400 hover:bg-amber-500/10 transition-colors" title="Edit result">
              <Pencil size={14} />
            </button>
          )}
          {isEmployee && r.approval_status === 'rejected' && (
            <button onClick={() => onResubmit(r)} className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium text-amber-400 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/20 transition-colors" title="Resubmit result">
              <Pencil size={12} /> Resubmit
            </button>
          )}
          {(isManager || isAdminOrHR) && r.approval_status === 'pending' && (
            <button onClick={() => onReview(r)} className="p-1.5 rounded-lg text-text-muted hover:text-emerald-400 hover:bg-emerald-500/10 transition-colors" title="Review submission">
              <Check size={14} />
            </button>
          )}
          {canDelete(r) && (
            <button onClick={() => onDelete(r)} className="p-1.5 rounded-lg text-text-muted hover:text-red-400 hover:bg-red-500/10 transition-colors" title="Delete result">
              <Trash2 size={14} />
            </button>
          )}
        </div>
      ),
    },
  ]

  return (
    <DataTable
      columns={columns}
      data={results}
      loading={loading}
      emptyTitle="No results yet"
      emptyDescription="Results will appear here once employees submit their actual values."
    />
  )
}