import { useState } from 'react'
import Modal from '@/components/ui/Modal'
import DeleteModal from '@/components/ui/DeleteModal'
import ModalButtons from '@/components/ui/ModalButtons'
import ApiError from '@/components/ui/ApiError'
import { Input } from '@/components/ui/FormField'
import { createDepartment, updateDepartment, deleteDepartment } from '@/services/orgService'
 
export default function DepartmentsTab({ depts, onRefresh, showSuccess }) {
  const [showCreate, setShowCreate]       = useState(false)
  const [editDept, setEditDept]           = useState(null)
  const [deleteDept, setDeleteDept]       = useState(null)
  const [form, setForm]                   = useState({ name: '', description: '' })
  const [loading, setLoading]             = useState(false)
  const [apiError, setApiError]           = useState('')
  const [deleteError, setDeleteError]     = useState('')
  const [deleteLoading, setDeleteLoading] = useState(false)

  const openCreate = () => {
    setForm({ name: '', description: '' })
    setApiError('')
    setShowCreate(true)
  }

  const openEdit = (d) => {
    setForm({ name: d.name, description: d.description || '' })
    setApiError('')
    setEditDept(d)
  }

  const handleSave = async () => {
    if (!form.name.trim()) { setApiError('Name is required'); return }
    setLoading(true)
    setApiError('')
    try {
      if (editDept) {
        await updateDepartment(editDept.uuid, form)
        showSuccess(`${form.name} updated`)
        setEditDept(null)
      } else {
        await createDepartment(form)
        showSuccess(`${form.name} created`)
        setShowCreate(false)
      }
      onRefresh()
    } catch (err) {
      setApiError(err.response?.data?.error || 'Failed to save department')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    setDeleteLoading(true)
    setDeleteError('')
    try {
      await deleteDepartment(deleteDept.uuid)
      showSuccess(`${deleteDept.name} deleted`)
      setDeleteDept(null)
      onRefresh()
    } catch (err) {
      setDeleteError(err.response?.data?.error || 'Failed to delete department')
    } finally {
      setDeleteLoading(false)
    }
  }

  return (
    <>
      {/* Toolbar */}
      <div className="flex items-center justify-between mb-4">
        <p className="text-slate-500 text-sm">
          {depts.length} {depts.length === 1 ? 'department' : 'departments'}
        </p>
        <button
          onClick={openCreate}
          className="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium rounded-lg transition-colors"
        >
          + Add Department
        </button>
      </div>

      {/* Table */}
      <div className="bg-[#1a1d27] border border-white/10 rounded-2xl overflow-hidden">
        <div className="grid grid-cols-[1fr_1fr_100px] px-6 py-3 border-b border-white/10">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Name</span>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Description</span>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Actions</span>
        </div>

        {depts.length === 0 && (
          <div className="flex items-center justify-center py-16">
            <p className="text-slate-600 text-sm italic">No departments yet</p>
          </div>
        )}

        {depts.map((dept, idx) => (
          <div
            key={dept.uuid}
            className={`grid grid-cols-[1fr_1fr_100px] px-6 py-4 items-center hover:bg-white/[0.025] transition-colors
              ${idx < depts.length - 1 ? 'border-b border-white/[0.06]' : ''}`}
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-violet-500/20 flex items-center justify-center text-violet-300 text-xs font-bold flex-shrink-0">
                {dept.name?.charAt(0).toUpperCase()}
              </div>
              <span className="text-white text-sm font-medium">{dept.name}</span>
            </div>

            <span className="text-slate-400 text-sm">
              {dept.description || <span className="text-slate-600 italic text-xs">No description</span>}
            </span>

            <div className="flex items-center gap-1">
              <button
                onClick={() => openEdit(dept)}
                className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                title="Edit"
              >✏️</button>
              <button
                onClick={() => { setDeleteDept(dept); setDeleteError('') }}
                className="p-2 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                title="Delete"
              >🗑️</button>
            </div>
          </div>
        ))}
      </div>

      {/* Create Modal */}
      {showCreate && (
        <Modal title="Add Department" onClose={() => setShowCreate(false)}>
          <ApiError message={apiError} />
          <Input
            label="Name"
            placeholder="e.g. Technology Department"
            value={form.name}
            onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
          />
          <Input
            label="Description"
            placeholder="Optional description"
            value={form.description}
            onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
          />
          <ModalButtons
            onCancel={() => setShowCreate(false)}
            onConfirm={handleSave}
            loading={loading}
            confirmLabel="Create"
          />
        </Modal>
      )}

      {/* Edit Modal */}
      {editDept && (
        <Modal title="Edit Department" onClose={() => setEditDept(null)}>
          <ApiError message={apiError} />
          <Input
            label="Name"
            value={form.name}
            onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
          />
          <Input
            label="Description"
            value={form.description}
            onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
          />
          <ModalButtons
            onCancel={() => setEditDept(null)}
            onConfirm={handleSave}
            loading={loading}
            confirmLabel="Save Changes"
          />
        </Modal>
      )}

      {/* Delete Modal */}
      {deleteDept && (
        <DeleteModal
          name={deleteDept.name}
          onClose={() => setDeleteDept(null)}
          onConfirm={handleDelete}
          loading={deleteLoading}
          error={deleteError}
        />
      )}
    </>
  )
}