import React from 'react'
import { Button, DataTable } from '../../components/ui'

export default function KpiFormulasTable({ formulas, loading, canManage, onEdit, onDelete, onCreateFirst }) {

  const columns = [
    { header: 'KPI',                key: 'kpi_name' },
    { header: 'Formula Expression', key: 'formula_expression' },
    { header: 'Data Source',        key: 'data_source' },
    { header: 'Created At',         key: 'created_at' },
    {
      header: 'Actions',
      render: (row) => canManage && (
        <div className="flex items-center gap-2">
          <button className="btn-secondary px-3 py-1 text-xs" onClick={() => onEdit(row)}>Edit</button>
          <button className="btn-danger px-3 py-1 text-xs" onClick={() => onDelete(row)}>Delete</button>
        </div>
      )
    },
  ]

  return (
    <DataTable
      columns={columns}
      data={formulas}
      loading={loading}
      emptyTitle="No formulas yet"
      emptyDescription="Add a formula to a KPI to define how it is calculated."
      emptyAction={canManage && <button className="btn-primary px-3 py-1 text-xs" onClick={onCreateFirst}>+ Add Formula</button>}
    />
  )
}
