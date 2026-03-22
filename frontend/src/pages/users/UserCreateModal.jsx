import { useState } from 'react'
import Modal from '@/components/ui/Modal'
import ModalButtons from '@/components/ui/ModalButtons'
import ApiError from '@/components/ui/ApiError'
import { Input, Select } from '@/components/ui/FormField'
import { createUser, assignRole, assignTeam } from '@/services/userService'

export default function UserCreateModal({ onClose, onCreated, roles, depts, teams }) {
  const [form, setForm] = useState({
    first_name:      '',
    last_name:       '',
    username:        '',
    email:           '',
    password:        '',
    role:            '',
    department_uuid: '',
    team_uuid:       '',
  })
  const [errors, setErrors]     = useState({})
  const [loading, setLoading]   = useState(false)
  const [apiError, setApiError] = useState('')

  const filteredTeams = form.department_uuid
    ? teams.filter(t => t.department_uuid === form.department_uuid)
    : teams

  const validate = () => {
    const e = {}
    if (!form.username.trim()) e.username = 'Username is required'
    if (!form.email.trim())    e.email    = 'Email is required'
    else if (!/\S+@\S+\.\S+/.test(form.email)) e.email = 'Invalid email'
    if (!form.password)        e.password = 'Password is required'
    else if (form.password.length < 8) e.password = 'Minimum 8 characters'
    return e
  }

  const handleSubmit = async () => {
    const e = validate()
    if (Object.keys(e).length) { setErrors(e); return }
    setLoading(true)
    setApiError('')
    try {
      const res = await createUser({
        username:   form.username,
        email:      form.email,
        password:   form.password,
        first_name: form.first_name,
        last_name:  form.last_name,
      })
      if (form.role) {
        await assignRole({ username: form.username, role_name: form.role })
      }
      if (form.team_uuid) {
        const newUser = res.data?.data
        if (newUser?.uuid) {
          await assignTeam({ user_uuid: newUser.uuid, team_uuid: form.team_uuid })
        }
      }
      onCreated(form.username)
    } catch (err) {
      setApiError(err.response?.data?.error || 'Failed to create user')
      setLoading(false)
    }
  }

  const set = (key) => (e) => setForm(f => ({ ...f, [key]: e.target.value }))

  return (
    <Modal title="Create New User" onClose={onClose}>
      <ApiError message={apiError} />

      <div className="grid grid-cols-2 gap-3">
        <Input label="First Name" placeholder="John"  value={form.first_name} onChange={set('first_name')} />
        <Input label="Last Name"  placeholder="Doe"   value={form.last_name}  onChange={set('last_name')} />
      </div>

      <Input label="Username" placeholder="e.g. john.doe"        value={form.username} onChange={set('username')} error={errors.username} />
      <Input label="Email"    placeholder="e.g. john@company.com" type="email" value={form.email} onChange={set('email')} error={errors.email} />
      <Input label="Password" placeholder="Min. 8 characters"     type="password" value={form.password} onChange={set('password')} error={errors.password} />

      <Select label="Role" value={form.role} onChange={set('role')}>
        <option value="">— Select role —</option>
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
        confirmLabel="Create User"
      />
    </Modal>
  )
}