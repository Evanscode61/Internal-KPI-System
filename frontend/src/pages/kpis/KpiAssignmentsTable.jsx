import React from 'react'
import { Button, DataTable } from '../../components/ui'

const EnterResultIcon = () => (
  <svg width="13" height="13" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
  </svg>
)

//  Determine if assignment is overdue
function isOverdue(assignment) {
  if (!assignment.period_end) return false
  const today     = new Date()
  const periodEnd = new Date(assignment.period_end)
  const isActive  = assignment.status?.toLowerCase() === 'active'
  return isActive && periodEnd < today
}

//Status badge that handles overdue
function AssignmentStatusBadge({ assignment }) {
  if (isOverdue(assignment)) {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium"
        style={{
          background: 'rgba(249,115,22,0.1)',
          color: '#fb923c',
          border: '1px solid rgba(249,115,22,0.2)'
        }}
      >
        <svg width="11" height="11" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
        </svg>
        Overdue
      </span>
    )
  }

  // Normal status badge
  const status = assignment.status?.toLowerCase() || ''
  const styles = {
    active:    { bg: 'rgba(34,197,94,0.1)',   color: '#4ade80', border: '1px solid rgba(34,197,94,0.2)'   },
    completed: { bg: 'rgba(59,130,246,0.1)',  color: '#60a5fa', border: '1px solid rgba(59,130,246,0.2)'  },
    inactive:  { bg: 'rgba(100,116,139,0.1)', color: '#94a3b8', border: '1px solid rgba(100,116,139,0.2)' },
  }
  const s = styles[status] || styles.inactive
  return (
    <span className="inline-block px-2.5 py-1 rounded-full text-xs font-medium capitalize"
      style={{ background: s.bg, color: s.color, border: s.border }}
    >
      {assignment.status || '—'}
    </span>
  )
}

export default function KpiAssignmentsTable({
  assignments, loading, canManage, onEdit, onDelete,
  onCreateFirst, onView, onEnterResult, isEmployee
}) {

  const columns = [
    { header: 'KPI', key: 'kpi_name' },
    {
      header: 'Assigned To',
      render: (row) => (
        <span className="text-text-secondary">
          {row.assigned_to_username || row.assigned_team_name || row.assigned_department_name || '—'}
        </span>
      )
    },
    { header: 'Period Start', key: 'period_start' },
    {
      header: 'Period End',
      render: (row) => (
        <span className={`text-sm ${isOverdue(row) ? 'text-amber-400 font-medium' : 'text-text-secondary'}`}>
          {row.period_end || '—'}
        </span>
      )
    },
    {
      header: 'Status',
      render: (row) => <AssignmentStatusBadge assignment={row} />
    },
    {
      header: 'Actions',
      render: (row) => (
        <div className="flex items-center gap-1.5">
          {/* View — everyone */}
          <Button variant="ghost" size="sm" onClick={() => onView(row)}>View</Button>

          {/* Enter Result — employee only, show for active or overdue */}
          {isEmployee && (
            <button
              onClick={() => onEnterResult(row)}
              className={`inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                isOverdue(row)
                  ? 'text-amber-400 bg-amber-500/10 hover:bg-amber-500/20 border-amber-500/20'
                  : 'text-brand-400 bg-brand-500/10 hover:bg-brand-500/20 border-brand-500/20'
              }`}
              title={isOverdue(row) ? 'This result is overdue — submit now' : 'Submit your result for this KPI'}
            >
              <EnterResultIcon />
              {isOverdue(row) ? 'Submit Now' : 'Enter Result'}
            </button>
          )}

          {/* Edit / Delete — managers and admin only */}
          {canManage && (
            <>
              <Button variant="ghost" size="sm" onClick={() => onEdit(row)}>Edit</Button>
              <Button variant="ghost" size="sm" className="hover:text-red-400" onClick={() => onDelete(row)}>Delete</Button>
            </>
          )}
        </div>
      )
    },
  ]

  return (
    <DataTable
      columns={columns}
      data={assignments}
      loading={loading}
      emptyTitle="No assignments yet"
      emptyDescription="Assign a KPI to a user, team or department to get started."
      emptyAction={canManage && <Button size="sm" onClick={onCreateFirst}>+ New Assignment</Button>}
    />
  )
}