import React, { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { performanceApi } from '../../api'
import { Modal, Button, Input, Select } from '../../components/ui'
import toast from 'react-hot-toast'

const EMPTY_FORM = {
  summaryType: 'individual',
  userUuid:    '',
  teamUuid:    '',
  deptUuid:    '',
  periodStart: '',
  periodEnd:   '',
}

export default function GenerateSummaryModal({
  open, onClose,
  isManager, isAdminOrHR,
  userList, teamList, deptList,
}) {
  const queryClient = useQueryClient()
  const [form, setForm] = useState(EMPTY_FORM)

  const set = (key, value) => setForm(prev => ({ ...prev, [key]: value }))
  const resetForm = () => setForm(EMPTY_FORM)
  const handleClose = () => { onClose(); resetForm() }

  const mutation = useMutation({
    mutationFn: (payload) => performanceApi.generateSummary(payload),
    onSuccess: () => {
      toast.success('Summary generated successfully')
      queryClient.invalidateQueries({ queryKey: ['performance-summaries'] })
      handleClose()
    },
    onError: (err) => {
      toast.error(err.response?.data?.message || err.response?.data?.error || 'Generation failed')
    },
  })

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

    mutation.mutate(payload)
  }

  return (
    <Modal open={open} onClose={handleClose} title="Generate Performance Summary" size="md">
      <div className="space-y-4">

        <Select label="Summary Type" value={form.summaryType} onChange={e => set('summaryType', e.target.value)}>
          <option value="individual">Individual Employee</option>
          {(isManager || isAdminOrHR) && <option value="team">Team</option>}
          {(isManager || isAdminOrHR) && <option value="department">Department</option>}
        </Select>

        {form.summaryType === 'individual' && (
          <Select label="Employee" value={form.userUuid} onChange={e => set('userUuid', e.target.value)}>
            <option value="">Select employee…</option>
            {userList.map(u => <option key={u.uuid} value={u.uuid}>{u.username}</option>)}
          </Select>
        )}

        {form.summaryType === 'team' && (
          <Select label="Team" value={form.teamUuid} onChange={e => set('teamUuid', e.target.value)}>
            <option value="">Select team…</option>
            {teamList.map(t => <option key={t.uuid} value={t.uuid}>{t.team_name}</option>)}
          </Select>
        )}

        {form.summaryType === 'department' && (
          <Select label="Department" value={form.deptUuid} onChange={e => set('deptUuid', e.target.value)}>
            <option value="">Select department…</option>
            {deptList.map(d => <option key={d.uuid} value={d.uuid}>{d.name}</option>)}
          </Select>
        )}

        <div className="grid grid-cols-2 gap-4">
          <Input label="Period Start" type="date" value={form.periodStart} onChange={e => set('periodStart', e.target.value)} />
          <Input label="Period End"   type="date" value={form.periodEnd}   onChange={e => set('periodEnd',   e.target.value)} />
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={handleClose} disabled={mutation.isPending}>Cancel</Button>
          <Button onClick={handleGenerate} loading={mutation.isPending}>Generate</Button>
        </div>

      </div>
    </Modal>
  )
}