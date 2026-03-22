import React, { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { kpiResultsApi } from '../../api'
import { useAuth } from '../../context/AuthContext'
import {
  Button, PageHeader, ErrorMessage, Modal, Input,
  RatingBadge, StatusBadge, ConfirmDialog, DetailRow,
} from '../../components/ui'
import { Download } from 'lucide-react'
import toast from 'react-hot-toast'
import KpiResultsTable   from './KpiResultsTable'
import SubmitResultModal from './SubmitResultModal'
import ReviewResultModal from './ReviewResultModal'

export default function KpiResultsPage() {
  const { user } = useAuth()
  const location  = useLocation()
  const queryClient = useQueryClient()

  const role        = user?.role || ''
  const isEmployee  = role === 'employee'
  const isManager   = role === 'Business_Line_Manager' || role === 'Tech_Line_Manager'
  const isAdminOrHR = role === 'admin' || role === 'hr'

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['kpi-results'],
    queryFn:  () => kpiResultsApi.list().then(r => r.data?.data ?? r.data ?? []),
  })

  const [viewTarget,   setViewTarget]   = useState(null)
  const [editTarget,   setEditTarget]   = useState(null)
  const [submitTarget, setSubmitTarget] = useState(null)
  const [reviewTarget, setReviewTarget] = useState(null)
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [actualValue,  setActualValue]  = useState('')
  const [search,       setSearch]       = useState('')

  useEffect(() => {
    const params = new URLSearchParams(location.search)
    const id = params.get('assignment_id')
    if (id) setSubmitTarget({ assignment_uuid: id })
  }, [location.search])

  const editMutation = useMutation({
    mutationFn: ({ uuid, value }) => kpiResultsApi.update(uuid, { actual_value: value }),
    onSuccess: () => {
      toast.success('Result updated successfully')
      queryClient.invalidateQueries({ queryKey: ['kpi-results'] })
      setEditTarget(null)
      setActualValue('')
    },
    onError: (err) => toast.error(err.response?.data?.message || 'Update failed'),
  })

  const deleteMutation = useMutation({
    mutationFn: (uuid) => kpiResultsApi.delete(uuid),
    onSuccess: () => {
      toast.success('Result deleted successfully')
      queryClient.invalidateQueries({ queryKey: ['kpi-results'] })
      setDeleteTarget(null)
    },
    onError: (err) => toast.error(err.response?.data?.message || 'Delete failed'),
  })

  const handleExport = async () => {
    try {
      const response = await kpiResultsApi.exportBlob()
      const url  = window.URL.createObjectURL(new Blob([response.data], { type: 'text/csv;charset=utf-8;' }))
      const link = document.createElement('a')
      link.href  = url
      link.setAttribute('download', 'kpi_results.csv')
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch {
      toast.error('Export failed')
    }
  }

  const canDelete = (r) => {
    if (role === 'admin') return true
    if ((isManager || isEmployee) && r.approval_status !== 'approved') return true
    return false
  }

  const resultList = Array.isArray(data) ? data : []
  const filtered   = resultList.filter(r =>
    r.kpi_name?.toLowerCase().includes(search.toLowerCase())     ||
    r.submitted_by?.toLowerCase().includes(search.toLowerCase()) ||
    r.department?.toLowerCase().includes(search.toLowerCase())
  )

  const total    = resultList.length
  const pending  = resultList.filter(r => r.approval_status === 'pending').length
  const approved = resultList.filter(r => r.approval_status === 'approved').length
  const rejected = resultList.filter(r => r.approval_status === 'rejected').length

  return (
    <div className="space-y-6">

      <PageHeader
        title="KPI Results"
        subtitle={`${total} total results`}
        actions={
          isAdminOrHR && (
            <Button variant="secondary" onClick={handleExport}>
              <Download size={15} /> Export CSV
            </Button>
          )
        }
      />

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: 'Total',    value: total,    color: '#818cf8' },
          { label: 'Pending',  value: pending,  color: '#fb923c' },
          { label: 'Approved', value: approved, color: '#4ade80' },
          { label: 'Rejected', value: rejected, color: '#f87171' },
        ].map(({ label, value, color }) => (
          <div key={label} className="card">
            <p className="text-xs text-text-muted uppercase tracking-wide">{label}</p>
            <p className="text-2xl font-bold mt-1" style={{ color }}>{value}</p>
          </div>
        ))}
      </div>

      {error && <ErrorMessage message={error?.message || 'Failed to load results'} onRetry={refetch} />}

      <input
        className="input max-w-xs"
        placeholder="Search KPI, employee, department…"
        value={search}
        onChange={e => setSearch(e.target.value)}
      />

      <KpiResultsTable
        results={filtered}
        loading={isLoading}
        isEmployee={isEmployee}
        isManager={isManager}
        isAdminOrHR={isAdminOrHR}
        canDelete={canDelete}
        onView={setViewTarget}
        onEdit={(r) => { setEditTarget(r); setActualValue(r.actual_value) }}
        onResubmit={(r) => setSubmitTarget({ assignment_uuid: r.assignment_uuid, isResubmit: true })}
        onReview={setReviewTarget}
        onDelete={setDeleteTarget}
      />

      {/* View Modal */}
      <Modal open={!!viewTarget} onClose={() => setViewTarget(null)} title="Result Details" size="md">
        {viewTarget && (
          <div className="space-y-4">
            <div className="bg-surface-muted rounded-lg p-4 space-y-3">
              <DetailRow label="KPI"        value={viewTarget.kpi_name} />
              <DetailRow label="Employee"   value={viewTarget.submitted_by || '—'} />
              <DetailRow label="Department" value={viewTarget.department   || '—'} />
              <DetailRow label="Target"     value={`${viewTarget.target ?? '—'} ${viewTarget.measurement_type || ''}`} />
              <DetailRow label="Actual"     value={`${parseFloat(viewTarget.actual_value).toFixed(1)} ${viewTarget.measurement_type || ''}`} />
              <DetailRow label="Score"      value={viewTarget.calculated_score ? `${parseFloat(viewTarget.calculated_score).toFixed(1)}%` : '—'} />
            </div>
            <div className="bg-surface-muted rounded-lg p-4 space-y-3">
              <DetailRow label="Period Start" value={viewTarget.period_start || '—'} />
              <DetailRow label="Period End"   value={viewTarget.period_end   || '—'} />
              <DetailRow label="Submitted"    value={viewTarget.created_at?.slice(0, 10) || '—'} />
              <div className="flex items-center justify-between">
                <span className="text-sm text-text-secondary">Rating</span>
                <RatingBadge rating={viewTarget.rating} />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-text-secondary">Approval Status</span>
                <StatusBadge status={viewTarget.approval_status} />
              </div>
            </div>
            {viewTarget.manager_comment && (
              <div className="bg-surface-muted rounded-lg p-4">
                <p className="text-xs text-text-muted uppercase tracking-wide mb-2">Manager Comment</p>
                <p className="text-sm text-text-primary">{viewTarget.manager_comment}</p>
                {viewTarget.reviewed_by && (
                  <p className="text-xs text-text-muted mt-2">— {viewTarget.reviewed_by}</p>
                )}
              </div>
            )}
            <div className="flex justify-end pt-2">
              <Button variant="secondary" onClick={() => setViewTarget(null)}>Close</Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Edit Modal */}
      <Modal
        open={!!editTarget}
        onClose={() => { setEditTarget(null); setActualValue('') }}
        title="Update Result"
        size="sm"
      >
        {editTarget && (
          <div className="space-y-4">
            <p className="text-sm text-text-secondary">
              Updating result for <span className="text-text-primary font-medium">{editTarget.kpi_name}</span>.
              You can only edit while the result is pending.
            </p>
            <Input
              label="New Actual Value"
              type="number"
              value={actualValue}
              onChange={e => setActualValue(e.target.value)}
              placeholder="Enter corrected value"
            />
            <div className="flex justify-end gap-3 pt-2">
              <Button variant="secondary" onClick={() => { setEditTarget(null); setActualValue('') }}>Cancel</Button>
              <Button onClick={() => editMutation.mutate({ uuid: editTarget.uuid, value: actualValue })} loading={editMutation.isPending}>
                Update
              </Button>
            </div>
          </div>
        )}
      </Modal>

      <SubmitResultModal target={submitTarget} onClose={() => setSubmitTarget(null)} />
      <ReviewResultModal target={reviewTarget} onClose={() => setReviewTarget(null)} />

      <ConfirmDialog
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => deleteMutation.mutate(deleteTarget.uuid)}
        title="Delete Result"
        message={`Are you sure you want to delete the result for "${deleteTarget?.kpi_name}"? This cannot be undone.`}
        confirmLabel="Delete"
        loading={deleteMutation.isPending}
      />

    </div>
  )
}