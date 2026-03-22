import RatingBadge from '@/components/ui/RatingBadge'

const ROLE_STYLES = {
  admin:                 'bg-violet-500/20 text-violet-300 border-violet-500/30',
  hr:                    'bg-blue-500/20 text-blue-300 border-blue-500/30',
  Business_Line_Manager: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  Tech_Line_Manager:     'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
  employee:              'bg-slate-500/20 text-slate-300 border-slate-500/30',
}

function RoleBadge({ role }) {
  const style = ROLE_STYLES[role] || 'bg-slate-500/20 text-slate-300 border-slate-500/30'
  return role ? (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs border font-medium ${style}`}>
      {role}
    </span>
  ) : (
    <span className="text-slate-600 text-xs italic">No role</span>
  )
}

const gridCols = 'grid-cols-[1.8fr_1.8fr_1.8fr_1.4fr_1.2fr_80px]'

export { gridCols }

export default function UserRow({ user, index, total, onEdit, onDelete }) {
  return (
    <div
      className={`grid ${gridCols} px-6 py-4 items-center hover:bg-white/[0.025] transition-colors
        ${index < total - 1 ? 'border-b border-white/[0.06]' : ''}`}
    >
      {/* Name + username */}
      <div className="flex items-center gap-3 min-w-0">
        <div className="w-8 h-8 rounded-full bg-violet-500/20 flex items-center justify-center text-violet-300 text-xs font-bold flex-shrink-0">
          {(user.first_name || user.username)?.charAt(0).toUpperCase()}
        </div>
        <div className="flex flex-col min-w-0">
          <span className="text-white text-sm font-medium truncate">
            {user.first_name || user.last_name
              ? `${user.first_name} ${user.last_name}`.trim()
              : user.username}
          </span>
          <span className="text-slate-500 text-xs truncate">@{user.username}</span>
        </div>
      </div>

      {/* Email */}
      <span className="text-slate-400 text-sm truncate pr-2">{user.email}</span>

      {/* Department */}
      <span className="text-slate-400 text-sm">
        {user.department__name || <span className="text-slate-600 italic text-xs">No dept</span>}
      </span>

      {/* Role */}
      <RoleBadge role={user.role__name} />

      {/* Team */}
      <span className="text-slate-400 text-sm">
        {user.team__team_name || <span className="text-slate-600 italic text-xs">No team</span>}
      </span>

      {/* Actions */}
      <div className="flex items-center gap-1">
        <button
          onClick={() => onEdit(user)}
          className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
          title="Edit user"
        >✏️</button>
        <button
          onClick={() => onDelete(user)}
          className="p-2 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-colors"
          title="Delete user"
        >🗑️</button>
      </div>
    </div>
  )
}