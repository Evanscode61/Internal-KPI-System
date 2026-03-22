import React, { useState } from 'react'
import { kpiDefinitionsApi } from '../../api'
import { Button, Modal } from '../../components/ui'
import toast from 'react-hot-toast'


export default function KpiDefinitionDeleteModal({ open, onClose, kpi, onSuccess }) {

  const [deleting, setDeleting] = useState(false)

  const handleDelete = async () => {
    setDeleting(true)
    try {
      await kpiDefinitionsApi.delete(kpi.uuid)
      toast.success(`"${kpi.kpi_name}" deleted`)
      onSuccess()
      onClose()
    } catch (err) {
      toast.error(err.response?.data?.error || 'Delete failed')
    } finally {
      setDeleting(false)
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="Delete KPI" size="sm">
      <div className="space-y-5">

        {/* Message */}
        <p className="text-text-secondary text-sm">
          Are you sure you want to delete{' '}
          <span className="text-text-primary font-semibold">"{kpi?.kpi_name}"</span>?
          This will also remove all assignments and results linked to it.
          This action cannot be undone.
        </p>

        {/* Buttons */}
        <div className="flex justify-end gap-3 pt-2 border-t border-surface-border">
          <Button variant="secondary" type="button" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDelete} loading={deleting}>
            Delete
          </Button>
        </div>

      </div>
    </Modal>
  )
}
