import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { performanceApi, usersApi, departmentsApi, teamsApi } from '../../api'
import { useAuth } from '../../context/AuthContext'
import {
  Button, PageHeader, ErrorMessage, DataTable,
  Modal, Input, Select, RatingBadge, ConfirmDialog
} from '../../components/ui'
import toast from 'react-hot-toast'

// ── Score badge
function ScoreBadge({ score }) {
  const s = parseFloat(score)
  if (isNaN(s)) return <span className="text-text-muted">—</span>
  const color = s >= 90 ? '#4ade80' : s >= 75 ? '#818cf8' : s >= 60 ? '#fb923c' : '#f87171'
  return <span style={{ color }} className="font-bold text-sm">{s.toFixed(1)}%</span>
}

// ── Score progress bar
function ScoreBar({ score }) {
  const s = Math.min(parseFloat(score) || 0, 100)
  const color = s >= 90 ? '#4ade80' : s >= 75 ? '#818cf8' : s >= 60 ? '#fb923c' : '#f87171'
  return (
    <div className="w-20 h-1.5 bg-surface-border rounded-full overflow-hidden">
      <div style={{ width: `${s}%`, backgroundColor: color }} className="h-full rounded-full" />
    </div>
  )
}

// ── Type badge
function TypeBadge({ type }) {
  const styles = {
    individual: { color: '#818cf8', bg: 'rgba(129,140,248,0.1)', border: '1px solid rgba(129,140,248,0.2)' },
    team:       { color: '#34d399', bg: 'rgba(52,211,153,0.1)',  border: '1px solid rgba(52,211,153,0.2)'  },
    department: { color: '#fb923c', bg: 'rgba(251,146,60,0.1)', border: '1px solid rgba(251,146,60,0.2)'  },
  }
  const s = styles[type] || styles.individual
  return (
    <span style={{
      color: s.color, background: s.bg, border: s.border,
      display: 'inline-block', padding: '2px 10px', borderRadius: '9999px',
      fontSize: '0.75rem', fontWeight: 500, textTransform: 'capitalize',
    }}>
      {type}
    </span>
  )
}

// ── Row helper
function Row({ label, value }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-text-secondary">{label}</span>
      <span className="text-sm text-text-primary font-medium">{value}</span>
    </div>
  )
}

// ── Icons
const DownloadIcon = () => (
  <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5 5-5M12 3v12" />
  </svg>
)
const PlusIcon = () => (
  <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
  </svg>
)
const EyeIcon = () => (
  <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
  </svg>
)
const TrashIcon = () => (
  <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
  </svg>
)
const SearchIcon = () => (
  <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M17 11A6 6 0 105 11a6 6 0 0012 0z" />
  </svg>
)

// ── Main Page
export default function PerformanceSummariesPage() {
  const { user, loading: authLoading } = useAuth()
  const queryClient = useQueryClient()

  const role        = user?.role || ''
  const isEmployee  = role === 'employee'
  const isManager   = role === 'Business_Line_Manager' || role === 'Tech_Line_Manager'
  const isAdminOrHR = role === 'admin' || role === 'hr'
  const canGenerate = isManager || isAdminOrHR

  // ── TanStack Query — data fetching with caching
  const { data: summariesData, isLoading, error, refetch } = useQuery({
    queryKey: ['performance-summaries'],
    queryFn:  () => performanceApi.listSummaries().then(r => r.data?.data ?? r.data ?? []),
    enabled:  !authLoading,
  })

  const { data: usersData } = useQuery({
    queryKey: ['users'],
    queryFn:  () => usersApi.list().then(r => r.data?.data ?? r.data ?? []),
    enabled:  canGenerate && !authLoading,
  })

  const { data: departmentsData } = useQuery({
    queryKey: ['departments'],
    queryFn:  () => departmentsApi.list().then(r => r.data?.data ?? r.data ?? []),
    enabled:  canGenerate && !authLoading,
  })

  const { data: teamsData } = useQuery({
    queryKey: ['teams'],
    queryFn:  () => teamsApi.list().then(r => r.data?.data ?? r.data ?? []),
    enabled:  canGenerate && !authLoading,
  })

  // ── TanStack Mutation — generate summary
  const generateMutation = useMutation({
    mutationFn: (payload) => performanceApi.generateSummary(payload),
    onSuccess: () => {
      toast.success('Summary generated successfully')
      queryClient.invalidateQueries({ queryKey: ['performance-summaries'] })
      setGenerateOpen(false)
      resetForm()
    },
    onError: (err) => {
      toast.error(err.response?.data?.message || err.response?.data?.error || 'Generation failed')
    },
  })

  // ── TanStack Mutation — delete summary
  const deleteMutation = useMutation({
    mutationFn: (uuid) => performanceApi.deleteSummary(uuid),
    onSuccess: () => {
      toast.success('Summary deleted successfully')
      queryClient.invalidateQueries({ queryKey: ['performance-summaries'] })
      setDeleteTarget(null)
    },
    onError: (err) => {
      toast.error(err.response?.data?.message || err.response?.data?.error || 'Delete failed')
    },
  })

  // ── Modal state
  const [viewTarget,   setViewTarget]   = useState(null)
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [generateOpen, setGenerateOpen] = useState(false)
  const [search,       setSearch]       = useState('')

  // ── Generate form — grouped into one object
  const [form, setForm] = useState({
    summaryType: 'individual',
    userUuid:    '',
    teamUuid:    '',
    deptUuid:    '',
    periodStart: '',
    periodEnd:   '',
  })

  const handleFormChange = (key, value) => setForm(prev => ({ ...prev, [key]: value }))
  const resetForm = () => setForm({
    summaryType: 'individual',
    userUuid: '', teamUuid: '', deptUuid: '',
    periodStart: '', periodEnd: '',
  })

  // ── Normalize data
  const summaryList = Array.isArray(summariesData) ? summariesData : []
  const userList    = Array.isArray(usersData)       ? usersData       : []
  const deptList    = Array.isArray(departmentsData) ? departmentsData : []
  const teamList    = Array.isArray(teamsData)       ? teamsData       : []

  // ── Filter
  const filtered = summaryList.filter(s =>
    s.username?.toLowerCase().includes(search.toLowerCase())        ||
    s.department_name?.toLowerCase().includes(search.toLowerCase()) ||
    s.team_name?.toLowerCase().includes(search.toLowerCase())       ||
    s.summary_type?.toLowerCase().includes(search.toLowerCase())
  )

  // ── Stats
  const total       = summaryList.length
  const outstanding = summaryList.filter(s => s.rating === 'outstanding').length
  const needsHelp   = summaryList.filter(s => s.rating === 'poor' || s.rating === 'needs_improvement').length
  const avgScore    = total
    ? (summaryList.reduce((acc, s) => acc + parseFloat(s.weighted_score || 0), 0) / total).toFixed(1)
    : '—'

  // ── Generate handler
  const handleGenerate = () => {
    const { summaryType, userUuid, teamUuid, deptUuid, periodStart, periodEnd } = form
    if (!periodStart || !periodEnd)                return toast.error('Please select a period')
    if (summaryType === 'individual' && !userUuid) return toast.error('Please select an employee')
    if (summaryType === 'team'       && !teamUuid) return toast.error('Please select a team')
    if (summaryType === 'department' && !deptUuid) return toast.error('Please select a department')
    if (periodEnd < periodStart)                   return toast.error('Period end must be after period start')

    const payload = { summary_type: summaryType, period_start: periodStart, period_end: periodEnd }
    if (summaryType === 'individual') payload.user_uuid       = userUuid
    if (summaryType === 'team')       payload.team_uuid       = teamUuid
    if (summaryType === 'department') payload.department_uuid = deptUuid

    generateMutation.mutate(payload)
  }

  // ── Export handler
  const handleExport = async () => {
    try {
      const response = await performanceApi.exportCsv()
      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'text/csv;charset=utf-8;' }))
      const link = document.createElement('a')
      link.href  = url
      link.setAttribute('download', 'performance_summaries.csv')
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      toast.success('CSV downloaded — open with Excel or Google Sheets')
    } catch {
      toast.error('Export failed')
    }
  }

  // ── Table columns
  const columns = [
    {
      header: 'Type',
      render: (s) => <TypeBadge type={s.summary_type} />
    },
    {
      header: 'Subject',
      render: (s) => (
        <span className="text-text-primary font-medium">
          {s.username || s.team_name || s.department_name || '—'}
        </span>
      )
    },
    ...(!isEmployee ? [{
      header: 'Department',
      render: (s) => <span className="text-text-secondary">{s.department_name || '—'}</span>
    }] : []),
    {
      header: 'Score',
      render: (s) => (
        <div className="flex items-center gap-2">
          <ScoreBadge score={s.weighted_score} />
          <ScoreBar   score={s.weighted_score} />
        </div>
      )
    },
    {
      header: 'Rating',
      render: (s) => <RatingBadge rating={s.rating} />
    },
    {
      header: 'KPIs',
      render: (s) => (
        <span className="text-text-secondary text-sm">
          {s.kpi_breakdown?.length ?? 0}
        </span>
      )
    },
    {
      header: 'Period',
      render: (s) => (
        <span className="text-text-muted text-xs whitespace-nowrap">
          {s.period_start} → {s.period_end}
        </span>
      )
    },
    {
      header: 'Generated',
      render: (s) => (
        <span className="text-text-muted text-xs">{s.created_at?.slice(0, 10) || '—'}</span>
      )
    },
    {
      header: 'Actions',
      render: (s) => (
        <div className="flex items-center gap-1">
          <button
            onClick={() => setViewTarget(s)}
            className="p-1.5 rounded-lg text-text-muted hover:text-brand-400 hover:bg-brand-500/10 transition-colors"
            title="View details"
          >
            <EyeIcon />
          </button>
          {(isManager || isAdminOrHR) && (
            <button
              onClick={() => setDeleteTarget(s)}
              className="p-1.5 rounded-lg text-text-muted hover:text-red-400 hover:bg-red-500/10 transition-colors"
              title="Delete summary"
            >
              <TrashIcon />
            </button>
          )}
        </div>
      )
    },
  ]

  return (
    <div className="space-y-6">

      <PageHeader
        title="Performance Summaries"
        subtitle={`${total} summaries generated`}
        actions={
          <div className="flex items-center gap-3">
            {isAdminOrHR && (
              <Button variant="secondary" onClick={handleExport}>
                <DownloadIcon /> Export CSV
              </Button>
            )}
            {canGenerate && (
              <Button onClick={() => setGenerateOpen(true)}>
                <PlusIcon /> Generate Summary
              </Button>
            )}
          </div>
        }
      />

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: 'Total',       value: total,                        color: '#818cf8' },
          { label: 'Outstanding', value: outstanding,                  color: '#4ade80' },
          { label: 'Needs Help',  value: needsHelp,                    color: '#f87171' },
          { label: 'Avg Score',   value: total ? `${avgScore}%` : '—', color: '#fb923c' },
        ].map(({ label, value, color }) => (
          <div key={label} className="card">
            <p className="text-xs text-text-muted uppercase tracking-wide">{label}</p>
            <p className="text-2xl font-bold mt-1" style={{ color }}>{value}</p>
          </div>
        ))}
      </div>

      {error && <ErrorMessage message={error?.message || 'Failed to load summaries'} onRetry={refetch} />}

      <div className="relative max-w-xs">
        <div className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none">
          <SearchIcon />
        </div>
        <input
          className="input pl-9"
          placeholder="Search by name, department, type…"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
      </div>

      <DataTable
        columns={columns}
        data={filtered}
        loading={isLoading}
        emptyTitle="No summaries yet"
        emptyDescription={
          canGenerate
            ? "Click Generate Summary to create a performance summary for an employee, team or department."
            : "Your performance summary will appear here once your manager generates it."
        }
      />

      {/* ── View Modal */}
      <Modal open={!!viewTarget} onClose={() => setViewTarget(null)} title="Performance Summary" size="lg">
        {viewTarget && (
          <div className="space-y-4">
            <div className="bg-surface-muted rounded-lg p-4 space-y-3">
              <Row label="Type"    value={<TypeBadge type={viewTarget.summary_type} />} />
              <Row label="Subject" value={viewTarget.username || viewTarget.team_name || viewTarget.department_name || '—'} />
              {viewTarget.department_name && <Row label="Department" value={viewTarget.department_name} />}
              {viewTarget.team_name       && <Row label="Team"       value={viewTarget.team_name} />}
              <Row label="Period Start" value={viewTarget.period_start} />
              <Row label="Period End"   value={viewTarget.period_end} />
              <Row label="Generated"    value={viewTarget.created_at?.slice(0, 10)} />
            </div>

            <div className="bg-surface-muted rounded-lg p-4">
              <p className="text-xs text-text-muted uppercase tracking-wide mb-3">Overall Performance</p>
              <div className="flex items-center justify-between mb-2">
                <span className="text-text-secondary text-sm">Weighted Score</span>
                <ScoreBadge score={viewTarget.weighted_score} />
              </div>
              <div className="w-full h-2 bg-surface-border rounded-full overflow-hidden mb-3">
                <div
                  style={{
                    width: `${Math.min(parseFloat(viewTarget.weighted_score) || 0, 100)}%`,
                    backgroundColor:
                      parseFloat(viewTarget.weighted_score) >= 90 ? '#4ade80'
                      : parseFloat(viewTarget.weighted_score) >= 75 ? '#818cf8'
                      : parseFloat(viewTarget.weighted_score) >= 60 ? '#fb923c'
                      : '#f87171'
                  }}
                  className="h-full rounded-full transition-all"
                />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-text-secondary text-sm">Rating</span>
                <RatingBadge rating={viewTarget.rating} />
              </div>
            </div>

            {viewTarget.kpi_breakdown?.length > 0 ? (
              <div className="bg-surface-muted rounded-lg p-4">
                <p className="text-xs text-text-muted uppercase tracking-wide mb-3">
                  KPI Breakdown ({viewTarget.kpi_breakdown.length} KPIs)
                </p>
                <div className="space-y-2">
                  <div className="grid grid-cols-4 gap-2 pb-2 border-b border-surface-border">
                    <span className="text-xs text-text-muted font-semibold uppercase">KPI</span>
                    <span className="text-xs text-text-muted font-semibold uppercase text-right">Score</span>
                    <span className="text-xs text-text-muted font-semibold uppercase text-right">Weight</span>
                    <span className="text-xs text-text-muted font-semibold uppercase text-right">Rating</span>
                  </div>
                  {viewTarget.kpi_breakdown.map((kpi, i) => (
                    <div key={i} className="grid grid-cols-4 gap-2 py-1.5 border-b border-surface-border/50 last:border-0">
                      <span className="text-sm text-text-primary truncate">{kpi.kpi_name}</span>
                      <span className="text-sm font-semibold text-right">
                        <ScoreBadge score={kpi.calculated_score} />
                      </span>
                      <span className="text-sm text-text-secondary text-right">{kpi.weight}×</span>
                      <div className="flex justify-end">
                        <RatingBadge rating={kpi.rating} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="bg-surface-muted rounded-lg p-4 text-center">
                <p className="text-sm text-text-muted">
                  No KPI breakdown available. This summary may have been generated before the breakdown feature was added. Delete and regenerate to see the full breakdown.
                </p>
              </div>
            )}

            <div className="flex justify-end pt-2">
              <Button variant="secondary" onClick={() => setViewTarget(null)}>Close</Button>
            </div>
          </div>
        )}
      </Modal>

      {/* ── Generate Modal */}
      <Modal
        open={generateOpen}
        onClose={() => { setGenerateOpen(false); resetForm() }}
        title="Generate Performance Summary"
        size="md"
      >
        <div className="space-y-4">
          <Select
            label="Summary Type"
            value={form.summaryType}
            onChange={e => handleFormChange('summaryType', e.target.value)}
          >
            <option value="individual">Individual Employee</option>
            {(isManager || isAdminOrHR) && <option value="team">Team</option>}
            {(isManager || isAdminOrHR) && <option value="department">Department</option>}
          </Select>

          {form.summaryType === 'individual' && (
            <Select
              label="Employee"
              value={form.userUuid}
              onChange={e => handleFormChange('userUuid', e.target.value)}
            >
              <option value="">Select employee…</option>
              {userList.map(u => (
                <option key={u.uuid} value={u.uuid}>{u.username}</option>
              ))}
            </Select>
          )}

          {form.summaryType === 'team' && (
            <Select
              label="Team"
              value={form.teamUuid}
              onChange={e => handleFormChange('teamUuid', e.target.value)}
            >
              <option value="">Select team…</option>
              {teamList.map(t => (
                <option key={t.uuid} value={t.uuid}>{t.team_name}</option>
              ))}
            </Select>
          )}

          {form.summaryType === 'department' && (
            <Select
              label="Department"
              value={form.deptUuid}
              onChange={e => handleFormChange('deptUuid', e.target.value)}
            >
              <option value="">Select department…</option>
              {deptList.map(d => (
                <option key={d.uuid} value={d.uuid}>{d.name}</option>
              ))}
            </Select>
          )}

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Period Start"
              type="date"
              value={form.periodStart}
              onChange={e => handleFormChange('periodStart', e.target.value)}
            />
            <Input
              label="Period End"
              type="date"
              value={form.periodEnd}
              onChange={e => handleFormChange('periodEnd', e.target.value)}
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <Button
              variant="secondary"
              onClick={() => { setGenerateOpen(false); resetForm() }}
              disabled={generateMutation.isPending}
            >
              Cancel
            </Button>
            <Button onClick={handleGenerate} loading={generateMutation.isPending}>
              Generate
            </Button>
          </div>
        </div>
      </Modal>

      {/* ── Delete Confirm Dialog */}
      <ConfirmDialog
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => deleteMutation.mutate(deleteTarget.uuid)}
        title="Delete Summary"
        message={`Are you sure you want to delete the ${deleteTarget?.summary_type} summary for "${deleteTarget?.username || deleteTarget?.team_name || deleteTarget?.department_name}"? This cannot be undone.`}
        confirmLabel="Delete"
        loading={deleteMutation.isPending}
      />

    </div>
  )
}