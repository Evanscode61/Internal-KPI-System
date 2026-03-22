import React, { useState, useEffect } from 'react'
import { kpiAssignmentsApi } from '../../api'
import { Button, Modal, Select, Input } from '../../components/ui'
import toast from 'react-hot-toast'

const EMPTY_FORM = {
  kpi_uuid:                 '',
  assigned_to_uuid:         '',
  assigned_team_uuid:       '',
  assigned_department_uuid: '',
  period_start:             '',
  period_end:               '',
  status:                   'active',
}

export default function KpiAssignmentModal({ open, onClose, editTarget, kpis, users, teams, departments, onSuccess }) {

  const [form, setForm]     = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    setForm(editTarget ? {
      kpi_uuid:                 editTarget.kpi_uuid                  || '',
      assigned_to_uuid:         editTarget.assigned_to_uuid          || '',
      assigned_team_uuid:       editTarget.assigned_team_uuid        || '',
      assigned_department_uuid: editTarget.assigned_department_uuid  || '',
      period_start:             editTarget.period_start              || '',
      period_end:               editTarget.period_end                || '',
      status:                   editTarget.status                    || 'active',
    } : EMPTY_FORM)
  }, [editTarget, open])

  const set = (field) => (e) => setForm(prev => ({ ...prev, [field]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.kpi_uuid)     return toast.error('Please select a KPI')
    if (!form.period_start) return toast.error('Period start is required')

    // Build payload — only include fields that have a value
    const payload = {
      kpi_uuid:     form.kpi_uuid,
      period_start: form.period_start,
    }
    if (form.period_end)               payload.period_end               = form.period_end
    if (form.status)                   payload.status                   = form.status
    if (form.assigned_to_uuid)         payload.assigned_to_uuid         = form.assigned_to_uuid
    if (form.assigned_team_uuid)       payload.assigned_team_uuid       = form.assigned_team_uuid
    if (form.assigned_department_uuid) payload.assigned_department_uuid = form.assigned_department_uuid

    console.log('Assignment payload:', payload)

    setSaving(true)
    try {
      if (editTarget) {
        await kpiAssignmentsApi.update(editTarget.uuid, payload)
        toast.success('Assignment updated')
      } else {
        await kpiAssignmentsApi.create(payload)
        toast.success('Assignment created')
      }
      onSuccess()
      onClose()
    } catch (err) {
      toast.error(err.response?.data?.error || 'Something went wrong')
    } finally {
      setSaving(false)
    }
  }

  const isEditing = !!editTarget

  return (
    <Modal open={open} onClose={onClose} title={isEditing ? 'Edit Assignment' : 'New Assignment'} size="md">
      <form onSubmit={handleSubmit} className="space-y-3">

        {/* KPI selector — disabled on edit, you cannot change which KPI is assigned */}
        <Select label="KPI *" value={form.kpi_uuid} onChange={set('kpi_uuid')} disabled={isEditing}>
          <option value="">— Select KPI —</option>
          {kpis.map(k => <option key={k.uuid} value={k.uuid}>{k.kpi_name}</option>)}
        </Select>

        <Select label="Assign to User (optional)" value={form.assigned_to_uuid} onChange={set('assigned_to_uuid')}>
          <option value="">— None —</option>
          {users.map(u => <option key={u.uuid} value={u.uuid}>{u.username}</option>)}
        </Select>

        <Select label="Assign to Team (optional)" value={form.assigned_team_uuid} onChange={set('assigned_team_uuid')}>
          <option value="">— None —</option>
          {teams.map(t => <option key={t.uuid} value={t.uuid}>{t.team_name}</option>)}
        </Select>

        <Select label="Assign to Department (optional)" value={form.assigned_department_uuid} onChange={set('assigned_department_uuid')}>
          <option value="">— None —</option>
          {departments.map(d => <option key={d.uuid} value={d.uuid}>{d.name}</option>)}
        </Select>

        <Select label="Status" value={form.status} onChange={set('status')}>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="completed">Completed</option>
        </Select>

        <Input label="Period Start *" type="date" value={form.period_start} onChange={set('period_start')} />
        <Input label="Period End" type="date" value={form.periodEnd} min={form.periodStart} onChange={e => handleChange('periodEnd', e.target.value)}/>

        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" type="button" onClick={onClose}>Cancel</Button>
          <Button type="submit" loading={saving}>{isEditing ? 'Save Changes' : 'Create'}</Button>
        </div>

      </form>
    </Modal>
  )
}
