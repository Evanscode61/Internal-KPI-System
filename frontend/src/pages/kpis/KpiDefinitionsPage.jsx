import React, { useState } from 'react'
import { kpiDefinitionsApi, departmentsApi, kpiFormulasApi } from '../../api'
import { useApi } from '../../hooks/useApi'
import { Button, PageHeader, ErrorMessage } from '../../components/ui'
import { useAuth } from '../../context/AuthContext'
import KpiDefinitionsTable      from './KpiDefinitionsTable'
import KpiDefinitionModal       from './KpiDefinitionModal'
import KpiDefinitionDeleteModal from './KpiDefinitionDeleteModal'
import KpiFormulaModal          from './KpiFormulaModal'

export default function KpiDefinitionsPage() {
  const { canManageKPIs, user } = useAuth()

  const { data: kpis, loading, error, refresh } = useApi(kpiDefinitionsApi.list)
  const { data: departments }                    = useApi(departmentsApi.list)

  const [formulaMap,      setFormulaMap]      = useState({})
  const [formulasLoading, setFormulasLoading] = useState(false)

  React.useEffect(() => {
    const kpiList = Array.isArray(kpis) ? kpis : []
    if (kpiList.length === 0) return
    setFormulasLoading(true)
    Promise.all(
      kpiList.map(k =>
        kpiFormulasApi.getByKpi(k.uuid)
          .then(res => ({ uuid: k.uuid, formula: res.data?.data ?? res.data }))
          .catch(() => ({ uuid: k.uuid, formula: null }))
      )
    )
    .then(results => {
      const map = {}
      results.forEach(({ uuid, formula }) => { if (formula) map[uuid] = formula })
      setFormulaMap(map)
    })
    .finally(() => setFormulasLoading(false))
  }, [kpis])

  const [modalOpen,    setModalOpen]    = useState(false)
  const [deleteOpen,   setDeleteOpen]   = useState(false)
  const [editTarget,   setEditTarget]   = useState(null)
  const [deleteTarget, setDeleteTarget] = useState(null)

  const [formulaModalOpen, setFormulaModalOpen] = useState(false)
  const [formulaTarget,    setFormulaTarget]    = useState(null)
  const [formulaKpi,       setFormulaKpi]       = useState(null)

  const [search, setSearch] = useState('')

  const kpiList  = Array.isArray(kpis)        ? kpis        : []
  const deptList = Array.isArray(departments) ? departments : []
  const filtered = kpiList.filter(k =>
    k.kpi_name?.toLowerCase().includes(search.toLowerCase()) ||
    k.department?.toLowerCase().includes(search.toLowerCase())
  )

  const handleOpenCreate  = () => { setEditTarget(null); setModalOpen(true) }
  const handleOpenEdit    = (kpi) => { setEditTarget(kpi); setModalOpen(true) }
  const handleOpenDelete  = (kpi) => { setDeleteTarget(kpi); setDeleteOpen(true) }
  const handleOpenFormula = (kpi) => {
    setFormulaKpi(kpi)
    setFormulaTarget(formulaMap[kpi.uuid] || null)
    setFormulaModalOpen(true)
  }

  const canManageFormula = ['Business_Line_Manager', 'Tech_Line_Manager'].includes(user?.role)

  return (
    <div className="space-y-6">
      <PageHeader
        title="KPI Definitions"
        subtitle={`${kpiList.length} KPIs defined`}
        actions={canManageKPIs() && <Button onClick={handleOpenCreate}>+ New KPI</Button>}
      />

      {error && <ErrorMessage message={error} onRetry={refresh} />}

      <input
        className="input max-w-xs"
        placeholder="Search by name or department…"
        value={search}
        onChange={e => setSearch(e.target.value)}
      />

      <KpiDefinitionsTable
        kpis={filtered}
        loading={loading || formulasLoading}
        canManage={canManageKPIs()}
        canManageFormula={canManageFormula}
        formulaMap={formulaMap}
        onEdit={handleOpenEdit}
        onDelete={handleOpenDelete}
        onCreateFirst={handleOpenCreate}
        onFormula={handleOpenFormula}
      />

      <KpiDefinitionModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        editTarget={editTarget}
        departments={deptList}
        onSuccess={() => refresh()}
      />

      <KpiDefinitionDeleteModal
        open={deleteOpen}
        onClose={() => setDeleteOpen(false)}
        kpi={deleteTarget}
        onSuccess={() => refresh()}
      />

      {formulaKpi && (
        <KpiFormulaModal
          open={formulaModalOpen}
          onClose={() => { setFormulaModalOpen(false); setFormulaKpi(null) }}
          editTarget={formulaTarget}
          kpis={[formulaKpi]}
          preselectedKpiUuid={formulaKpi?.uuid}
          onSuccess={() => refresh()}
        />
      )}
    </div>
  )
}