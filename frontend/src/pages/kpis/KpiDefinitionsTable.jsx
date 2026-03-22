import React from 'react'
import { Button, DataTable } from '../../components/ui'

const FREQUENCY_STYLES = {
  daily:     { background: 'rgba(239,68,68,0.1)',   color: '#f87171', border: '1px solid rgba(239,68,68,0.2)'   },
  weekly:    { background: 'rgba(249,115,22,0.1)',  color: '#fb923c', border: '1px solid rgba(249,115,22,0.2)'  },
  monthly:   { background: 'rgba(99,102,241,0.1)',  color: '#818cf8', border: '1px solid rgba(99,102,241,0.2)'  },
  quarterly: { background: 'rgba(168,85,247,0.1)',  color: '#c084fc', border: '1px solid rgba(168,85,247,0.2)'  },
  yearly:    { background: 'rgba(16,185,129,0.1)',  color: '#34d399', border: '1px solid rgba(16,185,129,0.2)'  },
}

function FrequencyBadge({ frequency }) {
  const style = FREQUENCY_STYLES[frequency] || { background: 'rgba(100,116,139,0.1)', color: '#94a3b8', border: '1px solid rgba(100,116,139,0.2)' }
  return (
    <span style={{ ...style, display: 'inline-block', padding: '2px 10px', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: 500, textTransform: 'capitalize' }}>
      {frequency || '—'}
    </span>
  )
}

function FormulaCell({ kpi, formula, canManageFormula, onFormula }) {
  const hasFormula = !!formula
  const pillStyle = hasFormula
    ? { background: 'rgba(16,185,129,0.1)', color: '#34d399', border: '1px solid rgba(16,185,129,0.2)' }
    : { background: 'rgba(100,116,139,0.1)', color: '#94a3b8', border: '1px solid rgba(100,116,139,0.2)' }

  return (
    <div className="flex flex-col gap-1">
      <span style={{ ...pillStyle, display: 'inline-block', padding: '2px 10px', borderRadius: '9999px', fontSize: '0.7rem', fontWeight: 500, width: 'fit-content' }}>
        {hasFormula ? '✓ Has Formula' : 'No Formula'}
      </span>
      {hasFormula && (
        <span className="text-xs text-text-muted max-w-[160px] truncate">{formula.formula_expression}</span>
      )}
      {canManageFormula && (
        <button onClick={() => onFormula(kpi)} className="text-xs text-brand-400 hover:text-brand-300 text-left w-fit">
          {hasFormula ? 'Edit formula →' : '+ Add formula'}
        </button>
      )}
    </div>
  )
}

export default function KpiDefinitionsTable({ kpis, loading, canManage, canManageFormula, formulaMap, onEdit, onDelete, onCreateFirst, onFormula }) {
  const columns = [
    {
      header: 'KPI Name',
      render: (row) => (
        <div>
          <div className="font-medium text-text-primary">{row.kpi_name}</div>
          {row.kpi_description && <div className="text-xs text-text-muted mt-0.5 max-w-xs truncate">{row.kpi_description}</div>}
        </div>
      )
    },
    { header: 'Department',  key: 'department' },
    { header: 'Frequency',   render: (row) => <FrequencyBadge frequency={row.frequency} /> },
    { header: 'Measurement', key: 'measurement_type' },
    { header: 'Weight',      key: 'weight_value' },
    {
      header: 'Formula',
      render: (row) => <FormulaCell kpi={row} formula={formulaMap?.[row.uuid] || null} canManageFormula={canManageFormula} onFormula={onFormula} />
    },
    {
      header: 'Actions',
      render: (row) => canManage && (
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={() => onEdit(row)}>Edit</Button>
          <Button variant="ghost" size="sm" className="hover:text-red-400" onClick={() => onDelete(row)}>Delete</Button>
        </div>
      )
    },
  ]

  return (
    <DataTable
      columns={columns}
      data={kpis}
      loading={loading}
      emptyTitle="No KPIs defined yet"
      emptyDescription="Create your first KPI definition to start tracking performance."
      emptyAction={canManage && <Button size="sm" onClick={onCreateFirst}>+ New KPI</Button>}
    />
  )
}