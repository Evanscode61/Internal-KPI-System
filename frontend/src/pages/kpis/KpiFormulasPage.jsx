import React, { useState } from 'react'
import { kpiFormulasApi, kpiDefinitionsApi } from '../../api'
import { useApi } from '../../hooks/useApi'
import { Button, PageHeader, ErrorMessage, ConfirmDialog } from '../../components/ui'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'
import KpiFormulasTable from './KpiFormulasTable'
import KpiFormulaModal from './KpiFormulaModal'

export default function KpiFormulasPage() {
  const { user } = useAuth()

  const { data: kpis, loading: kpisLoading, error, refresh: refreshKpis } = useApi(kpiDefinitionsApi.list)

  const [modalOpen,    setModalOpen]    = useState(false)
  const [editTarget,   setEditTarget]   = useState(null)
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [deleting,     setDeleting]     = useState(false)
  const [formulas,        setFormulas]        = useState([])
  const [formulasLoading, setFormulasLoading] = useState(false)
  const [search, setSearch] = useState('')

  React.useEffect(() => {
    if (!Array.isArray(kpis) || kpis.length === 0) return
    setFormulasLoading(true)
    Promise.all(
      kpis.map(k =>
        kpiFormulasApi.getByKpi(k.uuid)
          .then(res => res.data?.data ?? res.data)
          .catch(() => null)
      )
    )
    .then(results => setFormulas(results.filter(Boolean)))
    .finally(() => setFormulasLoading(false))
  }, [kpis])

  const refresh = () => refreshKpis()

  const handleOpenCreate = () => { setEditTarget(null); setModalOpen(true) }
  const handleOpenEdit   = (f) => { setEditTarget(f);   setModalOpen(true) }
  const handleOpenDelete = (f) => { setDeleteTarget(f) }

  const handleDelete = async () => {
    setDeleting(true)
    try {
      await kpiFormulasApi.delete(deleteTarget.uuid)
      toast.success('Formula deleted')
      setDeleteTarget(null)
      refresh()
    } catch (err) {
      toast.error(err.response?.data?.error || 'Delete failed')
    } finally {
      setDeleting(false)
    }
  }

  const canManage = ['Business_Line_Manager', 'Tech_Line_Manager'].includes(user?.role)
  const kpiList = Array.isArray(kpis) ? kpis : []
  const filtered = formulas.filter(f =>
    f.kpi_name?.toLowerCase().includes(search.toLowerCase()) ||
    f.formula_expression?.toLowerCase().includes(search.toLowerCase()) ||
    f.data_source?.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-6">
      <PageHeader
        title="KPI Formulas"
        subtitle={`${formulas.length} formulas defined`}
        actions={canManage && (
          <Button onClick={handleOpenCreate}>+ Add Formula</Button>
        )}
      />

      {error && <ErrorMessage message={error} onRetry={refresh} />}

      <input
        className="input max-w-xs"
        placeholder="Search by KPI or expression"
        value={search}
        onChange={e => setSearch(e.target.value)}
      />

      <KpiFormulasTable
        formulas={filtered}
        loading={kpisLoading || formulasLoading}
        canManage={canManage}
        onEdit={handleOpenEdit}
        onDelete={handleOpenDelete}
        onCreateFirst={handleOpenCreate}
      />

      <KpiFormulaModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        editTarget={editTarget}
        kpis={kpiList}
        onSuccess={refresh}
      />

      <ConfirmDialog
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        title="Delete Formula"
        message={`Are you sure you want to delete the formula for "${deleteTarget?.kpi_name}"? This cannot be undone.`}
        confirmLabel="Delete"
        loading={deleting}
      />
    </div>
  )
}