import React, { useState, useEffect } from 'react'
import { kpiDefinitionsApi } from '../../api'
import { Button, Modal } from '../../components/ui'
import toast from 'react-hot-toast'

const EMPTY_FORM = {
  kpi_name: '', kpi_description: '', frequency: 'monthly',
  measurement_type: '%', calculation_type: '', weight_value: '',
  min_threshold: '', max_threshold: '', department_uuid: '',
}

export default function KpiDefinitionModal({ open, onClose, editTarget, departments, onSuccess }) {
  const [form, setForm]         = useState(EMPTY_FORM)
  const [saving, setSaving]     = useState(false)
  const [showMore, setShowMore] = useState(false)

  useEffect(() => {
    setForm(editTarget ? {
      kpi_name:         editTarget.kpi_name         || '',
      kpi_description:  editTarget.kpi_description  || '',
      frequency:        editTarget.frequency         || 'monthly',
      measurement_type: editTarget.measurement_type || '%',
      calculation_type: editTarget.calculation_type || '',
      weight_value:     editTarget.weight_value      ?? '',
      min_threshold:    editTarget.min_threshold     ?? '',
      max_threshold:    editTarget.max_threshold     ?? '',
      department_uuid:  editTarget.department_uuid   || '',
    } : EMPTY_FORM)
    setShowMore(false)
  }, [editTarget, open])

  const set = (field) => (e) => setForm(prev => ({ ...prev, [field]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.kpi_name)         return toast.error('KPI name is required')
    if (!form.calculation_type) return toast.error('Calculation type is required')
    if (!form.weight_value)     return toast.error('Weight value is required')

    // ── Weight validation 1-10
    const weight = parseFloat(form.weight_value)
    if (isNaN(weight) || weight < 1 || weight > 10) {
      return toast.error('Weight must be between 1 and 10')
    }

    const payload = {
      kpi_name:         form.kpi_name,
      kpi_description:  form.kpi_description,
      frequency:        form.frequency,
      measurement_type: form.measurement_type,
      calculation_type: form.calculation_type,
      weight_value:     form.weight_value,
    }
    if (form.department_uuid) payload.department_uuid = form.department_uuid
    if (form.min_threshold)   payload.min_threshold   = form.min_threshold
    if (form.max_threshold)   payload.max_threshold   = form.max_threshold

    setSaving(true)
    try {
      if (editTarget) {
        await kpiDefinitionsApi.update(editTarget.uuid, payload)
        toast.success('KPI updated')
      } else {
        await kpiDefinitionsApi.create(payload)
        toast.success('KPI created')
      }
      onSuccess()
      onClose()
    } catch (err) {
      toast.error(err.response?.data?.error || 'Something went wrong')
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal open={open} onClose={onClose} title={editTarget ? 'Edit KPI' : 'Create KPI'} size="md">
      <form onSubmit={handleSubmit} className="space-y-3">

        {/* Required fields — always visible */}
        <div>
          <label className="label">KPI Name *</label>
          <input className="input" value={form.kpi_name} onChange={set('kpi_name')} />
        </div>

        <div>
          <label className="label">Measurement Type *</label>
          <input className="input" value={form.measurement_type} onChange={set('measurement_type')} />
        </div>

        <div>
          <label className="label">Weight Value * <span className="text-text-muted normal-case font-normal">(1 — 10)</span></label>
          <input
            className="input"
            type="number"
            min="1"
            max="10"
            step="0.5"
            value={form.weight_value}
            onChange={set('weight_value')}
            placeholder="e.g. 5"
          />
          <p className="text-xs text-text-muted mt-1">
            Higher weight means this KPI contributes more to the final performance score.
            <span className="text-brand-400 ml-1">1 = low importance · 10 = critical</span>
          </p>
        </div>

       <div>
  <label className="label">Calculation Type *</label>
  <select className="input" value={form.calculation_type} onChange={set('calculation_type')}>
    <option value="">— Select type —</option>
    <option value="percentage">Percentage — measured in %</option>
    <option value="time_based">Time Based — measured in hours or days</option>
    <option value="count_based">Count Based — measured in numbers</option>
    <option value="score_based">Score Based — measured by a score</option>
    <option value="ratio_based">Ratio Based — measured as a ratio</option>
  </select>
  <p className="text-xs text-text-muted mt-1">
    This determines how the KPI value is measured and interpreted.
  </p>
</div>

        <div>
          <label className="label">Frequency</label>
          <select className="input" value={form.frequency} onChange={set('frequency')}>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="quarterly">Quarterly</option>
            <option value="yearly">Yearly</option>
          </select>
        </div>

        <div>
          <label className="label">Department</label>
          <select className="input" value={form.department_uuid} onChange={set('department_uuid')}>
            <option value="">— None —</option>
            {departments.map(d => (
              <option key={d.uuid} value={d.uuid}>{d.name}</option>
            ))}
          </select>
        </div>

        {/* Advanced — hidden by default */}
        <button
          type="button"
          onClick={() => setShowMore(p => !p)}
          className="text-xs text-text-muted hover:text-text-secondary transition-colors"
        >
          {showMore ? '▲ Hide advanced fields' : '▼ Show advanced fields'}
        </button>

        {showMore && (
          <>
            <div>
              <label className="label">Min Threshold</label>
              <input className="input" type="number" step="0.01" value={form.min_threshold} onChange={set('min_threshold')} />
            </div>

            <div>
              <label className="label">Max Threshold</label>
              <input className="input" type="number" step="0.01" value={form.max_threshold} onChange={set('max_threshold')} />
            </div>

            <div>
              <label className="label">Description</label>
              <input className="input" value={form.kpi_description} onChange={set('kpi_description')} />
            </div>
          </>
        )}

        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" type="button" onClick={onClose}>Cancel</Button>
          <Button type="submit" loading={saving}>{editTarget ? 'Save Changes' : 'Create KPI'}</Button>
        </div>

      </form>
    </Modal>
  )
}