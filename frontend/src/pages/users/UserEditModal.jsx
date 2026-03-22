import { useState, useEffect } from 'react'
import Modal from '@/components/ui/Modal'
import ModalButtons from '@/components/ui/ModalButtons'
import ApiError from '@/components/ui/ApiError'
import { Input, Select } from '@/components/ui/FormField'
import { updateUser, assignTeam } from '@/services/userService'

export default function UserEditModal({ user, onClose, onUpdated, roles, depts, teams }) {
  const [form, setForm] = useState({
    first_name:      user.first_name      || '',
    last_name:       user.last_name       || '',
    username:        user.username        || '',
    email:           user.email           || '',
    role:            user.role__name      || '',
    department_uuid: '',
    team_uuid:       '',
  })
  const [errors, setErrors]     = useState({})
  const [loading, setLoading]   = useState(false)
  const [apiError, setApiError] = useState('')

  // pre-select current department and team once options load
  useEffect(() => {
    const currentDept = depts.find(d => d.name === user.department__name)
    const currentTeam = teams.find(t => t.team_name === user.team__team_name)
    setForm(f => ({
      ...f,
      department_uuid: currentDept?.uuid || '',
      team_uuid:       currentTeam?.uuid || '',
    }))
  }, [depts, teams])

  const filteredTeams = form.department_uuid
    ? teams.filter(t => t.department_uuid === form.department_uuid)
    : teams

  const validate = () => {
    const e = {}
    if (!form.username.trim()) e.username = 'Username is required'
    if (!form.email.trim())    e.email    = 'Email is required'
    else if (!/\S+@\S+\.\S+/.test(form.email)) e.email = 'Invalid email'
    return e
  }

  const handleSubmit = async () => {
    const e = validate()
    if (Object.keys(e).length) { setErrors(e); return }
    setLoading(true)
    setApiError('')
    try {
      const payload = {
        first_name: form.first_name,
        last_name:  form.last_name,
        username:   form.username,
        email:      form.email,
      }
      if (form.role) payload.role = form.role
      await updateUser(user.uuid, payload)

      if (form.team_uuid) {
        await assignTeam({ user_uuid: user.uuid, team_uuid: form.team_uuid })
      }
      onUpdated(form.username)
    } catch (err) {
      setApiError(err.response?.data?.error || 'Failed to update user')
      setLoading(false)
    }
  }

  const set = (key) => (e) => setForm(f => ({ ...f, [key]: e.target.value }))

  return (
    <Modal title="Edit User" onClose={onClose}>
      <ApiError message={apiError} />

      <div className="grid grid-cols-2 gap-3">
        <Input label="First Name" value={form.first_name} onChange={set('first_name')} />
        <Input label="Last Name"  value={form.last_name}  onChange={set('last_name')} />
      </div>

      <Input label="Username" value={form.username} onChange={set('username')} error={errors.username} />
      <Input label="Email"    value={form.email}    onChange={set('email')}    error={errors.email} type="email" />

      <Select label="Role" value={form.role} onChange={set('role')}>
        <option value="">— Keep current role —</option>
        {roles.map(r => <option key={r} value={r}>{r}</option>)}
      </Select>

      <Select label="Department" value={form.department_uuid}
        onChange={e => setForm(f => ({ ...f, department_uuid: e.target.value, team_uuid: '' }))}>
        <option value="">— Select department —</option>
        {depts.map(d => <option key={d.uuid} value={d.uuid}>{d.name}</option>)}
      </Select>

      <Select label="Team" value={form.team_uuid} onChange={set('team_uuid')}>
        <option value="">— Select team —</option>
        {filteredTeams.map(t => <option key={t.uuid} value={t.uuid}>{t.team_name}</option>)}
      </Select>

      <ModalButtons
        onCancel={onClose}
        onConfirm={handleSubmit}
        loading={loading}
        confirmLabel="Save Changes"
      />
    </Modal>
  )
}