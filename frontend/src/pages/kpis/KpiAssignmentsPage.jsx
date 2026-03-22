import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { kpiAssignmentsApi, kpiDefinitionsApi, departmentsApi, teamsApi, usersApi } from '../../api'
import { useApi } from '../../hooks/useApi'
import { Button, PageHeader, ErrorMessage, ConfirmDialog, Modal, StatusBadge } from '../../components/ui'
import { useAuth } from '../../context/AuthContext'
import KpiAssignmentsTable from './KpiAssignmentsTable'
import KpiAssignmentModal  from './KpiAssignmentModal'
import toast from 'react-hot-toast'

export default function KpiAssignmentsPage() {

  const { user, canManageKPIs } = useAuth()
  const navigate = useNavigate()

  const role       = user?.role || ''
  const isEmployee = role === 'employee'

  // ── Data fetching
  const { data: assignments, loading, error, refresh } = useApi(kpiAssignmentsApi.list)
  const { data: kpis }        = useApi(kpiDefinitionsApi.list)
  const { data: departments } = useApi(departmentsApi.list)
  const { data: teams }       = useApi(teamsApi.list)
  const { data: users }       = useApi(usersApi.list)

  // ── Modal state
  const [modalOpen,    setModalOpen]    = useState(false)
  const [editTarget,   setEditTarget]   = useState(null)
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [deleting,     setDeleting]     = useState(false)
  const [viewTarget,   setViewTarget]   = useState(null)
  const [search,       setSearch]       = useState('')

  // ── Normalize API responses
  const assignmentList = Array.isArray(assignments) ? assignments : []
  const kpiList        = Array.isArray(kpis)        ? kpis        : []
  const deptList       = Array.isArray(departments) ? departments : []
  const teamList       = Array.isArray(teams)       ? teams       : []
  const userList       = Array.isArray(users)       ? users       : []

  // ── Filter
  const filtered = assignmentList.filter(a =>
    a.kpi_name?.toLowerCase().includes(search.toLowerCase()) ||
    a.assigned_to_username?.toLowerCase().includes(search.toLowerCase()) ||
    a.assigned_team_name?.toLowerCase().includes(search.toLowerCase()) ||
    a.assigned_department_name?.toLowerCase().includes(search.toLowerCase())
  )

  // ── Handlers
  const handleOpenCreate  = ()  => { setEditTarget(null); setModalOpen(true) }
  const handleOpenEdit    = (a) => { setEditTarget(a);    setModalOpen(true) }
  const handleOpenDelete  = (a) => { setDeleteTarget(a) }
  const handleOpenView    = (a) => { setViewTarget(a) }
  const handleEnterResult = (a) => { navigate(`/kpi-results?assignment_id=${a.uuid}`) }

  const handleDelete = async () => {
    setDeleting(true)
    try {
      await kpiAssignmentsApi.delete(deleteTarget.uuid)
      toast.success('Assignment deleted')
      setDeleteTarget(null)
      refresh()
    } catch (err) {
      toast.error(err.response?.data?.error || 'Delete failed')
    } finally {
      setDeleting(false)
    }
  }

  return (
    <div className="space-y-6">

      <PageHeader
        title="KPI Assignments"
        subtitle={`${assignmentList.length} assignments`}
        actions={canManageKPIs() && (
          <Button onClick={handleOpenCreate}>+ New Assignment</Button>
        )}
      />

      {error && <ErrorMessage message={error} onRetry={refresh} />}

      <input
        className="input max-w-xs"
        placeholder="Search by KPI or assignee…"
        value={search}
        onChange={e => setSearch(e.target.value)}
      />

      <KpiAssignmentsTable
        assignments={filtered}
        loading={loading}
        canManage={canManageKPIs()}
        onEdit={handleOpenEdit}
        onDelete={handleOpenDelete}
        onCreateFirst={handleOpenCreate}
        onView={handleOpenView}
        onEnterResult={handleEnterResult}
        isEmployee={isEmployee}
      />

      {/* ── View Modal */}
      <Modal open={!!viewTarget} onClose={() => setViewTarget(null)} title="Assignment Details" size="md">
        {viewTarget && (
          <div className="space-y-4">

            {/* KPI Information */}
            <div className="bg-surface-muted rounded-lg p-4 space-y-3">
              <p className="text-xs text-text-muted uppercase tracking-wide font-semibold">KPI Information</p>
              <Row label="KPI Name"    value={viewTarget.kpi_name} />
              {viewTarget.kpi_description && (
                <Row label="Description" value={viewTarget.kpi_description} />
              )}
              <Row label="Measurement" value={viewTarget.measurement_type || '—'} />
              <Row label="Weight"      value={viewTarget.weight_value ? `${viewTarget.weight_value} / 10` : '—'} />
            </div>

            {/* Target & Thresholds */}
            <div className="bg-surface-muted rounded-lg p-4 space-y-3">
              <p className="text-xs text-text-muted uppercase tracking-wide font-semibold">Target & Thresholds</p>
              <Row
                label="Target Value"
                value={viewTarget.max_threshold
                  ? `${viewTarget.max_threshold} ${viewTarget.measurement_type || ''}`
                  : '—'}
              />
              <Row
                label="Min Threshold"
                value={viewTarget.min_threshold
                  ? `${viewTarget.min_threshold} ${viewTarget.measurement_type || ''}`
                  : '—'}
              />
            </div>

            {/* Assignment Details */}
            <div className="bg-surface-muted rounded-lg p-4 space-y-3">
              <p className="text-xs text-text-muted uppercase tracking-wide font-semibold">Assignment Details</p>
              <Row label="Assigned To" value={
                viewTarget.assigned_to_username ||
                viewTarget.assigned_team_name ||
                viewTarget.assigned_department_name || '—'
              } />
              {viewTarget.assigned_team_name && (
                <Row label="Team" value={viewTarget.assigned_team_name} />
              )}
              {viewTarget.assigned_department_name && (
                <Row label="Department" value={viewTarget.assigned_department_name} />
              )}
              <Row label="Period Start" value={viewTarget.period_start || '—'} />
              <Row label="Period End"   value={viewTarget.period_end   || '—'} />
              <div className="flex items-center justify-between">
                <span className="text-sm text-text-secondary">Status</span>
                <StatusBadge status={viewTarget.status} />
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <Button variant="secondary" onClick={() => setViewTarget(null)}>Close</Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Create / Edit Modal */}
      <KpiAssignmentModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        editTarget={editTarget}
        kpis={kpiList}
        users={userList}
        teams={teamList}
        departments={deptList}
        onSuccess={refresh}
      />

      {/* Delete */}
      <ConfirmDialog
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        title="Delete Assignment"
        message={`Are you sure you want to delete the assignment for "${deleteTarget?.kpi_name}"? This cannot be undone.`}
        confirmLabel="Delete"
        loading={deleting}
      />

    </div>
  )
}

function Row({ label, value }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-text-secondary">{label}</span>
      <span className="text-sm text-text-primary font-medium">{value}</span>
    </div>
  )
}