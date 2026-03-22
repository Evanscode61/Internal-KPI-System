import { useState, useEffect } from 'react'
import Toast from '@/components/ui/Toast'
import UserRow, { gridCols } from './UserRow'
import UserCreateModal from './UserCreateModal'
import UserEditModal from './UserEditModal'
import UserDeleteModal from './UserDeleteModal'
import { getUsers, getRoles, getDepts, getTeams } from '@/services/userService'

export default function UsersPage() {
  const [users, setUsers]           = useState([])
  const [roles, setRoles]           = useState([])
  const [depts, setDepts]           = useState([])
  const [teams, setTeams]           = useState([])
  const [loading, setLoading]       = useState(true)
  const [error, setError]           = useState('')
  const [search, setSearch]         = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [editUser, setEditUser]     = useState(null)
  const [deleteUser, setDeleteUser] = useState(null)
  const [successMsg, setSuccessMsg] = useState('')

  const fetchUsers = () => {
    setLoading(true)
    getUsers()
      .then(res => {
        const data = res.data?.data ?? res.data?.message ?? []
        setUsers(Array.isArray(data) ? data : [])
      })
      .catch(() => setError('Failed to load users'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchUsers()
    Promise.all([getRoles(), getDepts(), getTeams()]).then(([r, d, t]) => {
      setRoles(r.data?.data || [])
      setDepts(d.data?.data || [])
      setTeams(t.data?.data || [])
    })
  }, [])

  const showSuccess = (msg) => {
    setSuccessMsg(msg)
    setTimeout(() => setSuccessMsg(''), 3000)
  }

  const handleCreated = (username) => { setShowCreate(false); showSuccess(`${username} created`); fetchUsers() }
  const handleUpdated = (username) => { setEditUser(null);    showSuccess(`${username} updated`); fetchUsers() }
  const handleDeleted = (username) => { setDeleteUser(null);  showSuccess(`${username} deleted`); fetchUsers() }

  const filtered = users.filter(u => {
    const q = search.toLowerCase()
    return (
      u.username?.toLowerCase().includes(q)        ||
      u.email?.toLowerCase().includes(q)           ||
      (u.first_name       || '').toLowerCase().includes(q) ||
      (u.last_name        || '').toLowerCase().includes(q) ||
      (u.role__name       || '').toLowerCase().includes(q) ||
      (u.department__name || '').toLowerCase().includes(q) ||
      (u.team__team_name  || '').toLowerCase().includes(q)
    )
  })

  return (
    <div className="p-6 flex flex-col gap-6">
      <Toast message={successMsg} />

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-white text-xl font-semibold tracking-tight">Users</h1>
          <p className="text-slate-500 text-sm mt-1">Manage accounts and role assignments</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="px-4 py-2.5 bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium rounded-lg transition-colors"
        >
          + Create User
        </button>
      </div>

      {/* Search */}
      <div className="flex items-center gap-4">
        <div className="relative max-w-sm w-full">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 text-sm">🔍</span>
          <input
            className="w-full bg-[#1a1d27] border border-white/10 rounded-lg pl-9 pr-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-violet-500/60 focus:ring-1 focus:ring-violet-500/30 transition-all"
            placeholder="Search by name, email, role, team..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        {!loading && (
          <span className="text-slate-500 text-sm">
            {filtered.length} {filtered.length === 1 ? 'user' : 'users'}
          </span>
        )}
      </div>

      {/* Table */}
      <div className="bg-[#1a1d27] border border-white/10 rounded-2xl overflow-hidden">

        {/* Column headers */}
        <div className={`grid ${gridCols} px-6 py-3 border-b border-white/10`}>
          {['Name', 'Email', 'Department', 'Role', 'Team', 'Actions'].map(col => (
            <span key={col} className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{col}</span>
          ))}
        </div>

        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="w-6 h-6 border-2 border-violet-500/30 border-t-violet-500 rounded-full animate-spin" />
          </div>
        )}

        {!loading && error && (
          <div className="flex items-center justify-center py-20">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        {!loading && !error && filtered.length === 0 && (
          <div className="flex items-center justify-center py-20">
            <p className="text-slate-600 text-sm">
              {search ? `No users match "${search}"` : 'No users found'}
            </p>
          </div>
        )}

        {!loading && !error && filtered.map((user, idx) => (
          <UserRow
            key={user.uuid}
            user={user}
            index={idx}
            total={filtered.length}
            onEdit={setEditUser}
            onDelete={setDeleteUser}
          />
        ))}
      </div>

      {/* Modals */}
      {showCreate && (
        <UserCreateModal
          onClose={() => setShowCreate(false)}
          onCreated={handleCreated}
          roles={roles}
          depts={depts}
          teams={teams}
        />
      )}
      {editUser && (
        <UserEditModal
          user={editUser}
          onClose={() => setEditUser(null)}
          onUpdated={handleUpdated}
          roles={roles}
          depts={depts}
          teams={teams}
        />
      )}
      {deleteUser && (
        <UserDeleteModal
          user={deleteUser}
          onClose={() => setDeleteUser(null)}
          onDeleted={handleDeleted}
        />
      )}
    </div>
  )
}