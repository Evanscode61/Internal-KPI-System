import { useState } from 'react'
import Modal from '@/components/ui/Modal'
import DeleteModal from '@/components/ui/DeleteModal'
import ModalButtons from '@/components/ui/ModalButtons'
import ApiError from '@/components/ui/ApiError'
import { Input, Select } from '@/components/ui/FormField'
import { createTeam, updateTeam, deleteTeam } from '@/services/orgService'

export default function TeamsTab({ teams, depts, onRefresh, showSuccess }) {
  const [showCreate, setShowCreate]       = useState(false)
  const [editTeam, setEditTeam]           = useState(null)
  const [deleteTeam_, setDeleteTeam]      = useState(null)
  const [form, setForm]                   = useState({ team_name: '', department_uuid: '' })
  const [loading, setLoading]             = useState(false)
  const [apiError, setApiError]           = useState('')
  const [deleteError, setDeleteError]     = useState('')
  const [deleteLoading, setDeleteLoading] = useState(false)

  const openCreate = () => {
    setForm({ team_name: '', department_uuid: '' })
    setApiError('')
    setShowCreate(true)
  }

  const openEdit = (t) => {
    setForm({ team_name: t.team_name, department_uuid: t.department_uuid })
    setApiError('')
    setEditTeam(t)
  }

  const handleSave = async () => {
    if (!form.team_name.trim())  { setApiError('Team name is required'); return }
    if (!form.department_uuid)   { setApiError('Department is required'); return }
    setLoading(true)
    setApiError('')
    try {
      if (editTeam) {
        await updateTeam(editTeam.uuid, form)
        showSuccess(`${form.team_name} updated`)
        setEditTeam(null)
      } else {
        await createTeam(form)
        showSuccess(`${form.team_name} created`)
        setShowCreate(false)
      }
      onRefresh()
    } catch (err) {
      setApiError(err.response?.data?.error || 'Failed to save team')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    setDeleteLoading(true)
    setDeleteError('')
    try {
      await deleteTeam(deleteTeam_.uuid)
      showSuccess(`${deleteTeam_.team_name} deleted`)
      setDeleteTeam(null)
      onRefresh()
    } catch (err) {
      setDeleteError(err.response?.data?.error || 'Failed to delete team')
    } finally {
      setDeleteLoading(false)
    }
  }

  // Group teams by department
  const grouped = depts.map(d => ({
    ...d,
    teams: teams.filter(t => t.department_uuid === d.uuid)
  }))

  const TeamForm = () => (
    <>
      <ApiError message={apiError} />
      <Input
        label="Team Name"
        placeholder="e.g. Frontend Team"
        value={form.team_name}
        onChange={e => setForm(f => ({ ...f, team_name: e.target.value }))}
      />
      <Select
        label="Department"
        value={form.department_uuid}
        onChange={e => setForm(f => ({ ...f, department_uuid: e.target.value }))}
      >
        <option value="">— Select department —</option>
        {depts.map(d => <option key={d.uuid} value={d.uuid}>{d.name}</option>)}
      </Select>
    </>
  )

  return (
    <>
      {/* Toolbar */}
      <div className="flex items-center justify-between mb-4">
        <p className="text-slate-500 text-sm">
          {teams.length} {teams.length === 1 ? 'team' : 'teams'}
        </p>
        <button
          onClick={openCreate}
          className="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium rounded-lg transition-colors"
        >
          + Add Team
        </button>
      </div>

      {/* Grouped list */}
      <div className="flex flex-col gap-4">
        {grouped.map(dept => dept.teams.length > 0 && (
          <div key={dept.uuid} className="bg-[#1a1d27] border border-white/10 rounded-2xl overflow-hidden">

            {/* Department header */}
            <div className="flex items-center gap-3 px-6 py-3 border-b border-white/10 bg-white/[0.02]">
              <div className="w-6 h-6 rounded-md bg-violet-500/20 flex items-center justify-center text-violet-300 text-xs font-bold">
                {dept.name?.charAt(0).toUpperCase()}
              </div>
              <span className="text-white text-sm font-semibold">{dept.name}</span>
              <span className="ml-auto text-slate-500 text-xs">
                {dept.teams.length} {dept.teams.length === 1 ? 'team' : 'teams'}
              </span>
            </div>

            {/* Team rows */}
            {dept.teams.map((team, idx) => (
              <div
                key={team.uuid}
                className={`flex items-center justify-between px-6 py-4 hover:bg-white/[0.025] transition-colors
                  ${idx < dept.teams.length - 1 ? 'border-b border-white/[0.06]' : ''}`}
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center text-blue-300 text-xs font-bold flex-shrink-0">
                    {team.team_name?.charAt(0).toUpperCase()}
                  </div>
                  <span className="text-white text-sm font-medium">{team.team_name}</span>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => openEdit(team)}
                    className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                    title="Edit"
                  >✏️</button>
                  <button
                    onClick={() => { setDeleteTeam(team); setDeleteError('') }}
                    className="p-2 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                    title="Delete"
                  >🗑️</button>
                </div>
              </div>
            ))}
          </div>
        ))}

        {teams.length === 0 && (
          <div className="flex items-center justify-center py-16 bg-[#1a1d27] border border-white/10 rounded-2xl">
            <p className="text-slate-600 text-sm italic">No teams yet</p>
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showCreate && (
        <Modal title="Add Team" onClose={() => setShowCreate(false)}>
          <TeamForm />
          <ModalButtons
            onCancel={() => setShowCreate(false)}
            onConfirm={handleSave}
            loading={loading}
            confirmLabel="Create"
          />
        </Modal>
      )}

      {/* Edit Modal */}
      {editTeam && (
        <Modal title="Edit Team" onClose={() => setEditTeam(null)}>
          <TeamForm />
          <ModalButtons
            onCancel={() => setEditTeam(null)}
            onConfirm={handleSave}
            loading={loading}
            confirmLabel="Save Changes"
          />
        </Modal>
      )}

      {/* Delete Modal */}
      {deleteTeam_ && (
        <DeleteModal
          name={deleteTeam_.team_name}
          onClose={() => setDeleteTeam(null)}
          onConfirm={handleDelete}
          loading={deleteLoading}
          error={deleteError}
        />
      )}
    </>
  )
}