import RatingBadge from '@/components/ui/RatingBadge'

export default function NeedsAttention({ users }) {
  if (!users?.length) return null

  return (
    <div className="bg-[#1a1d27] border border-red-500/20 rounded-2xl p-5 flex flex-col gap-4">
      <div className="flex items-center gap-2">
        <span className="text-lg">⚠️</span>
        <h2 className="text-white font-semibold text-sm">Needs Attention</h2>
        <span className="ml-auto bg-red-500/20 text-red-400 text-xs font-medium px-2.5 py-1 rounded-full">
          {users.length} {users.length === 1 ? 'user' : 'users'}
        </span>
      </div>

      <div className="flex flex-col gap-3">
        {users.map(u => (
          <div key={u.user_uuid} className="flex items-center gap-3 bg-red-500/5 border border-red-500/10 rounded-xl px-4 py-3">
            <div className="w-8 h-8 rounded-full bg-red-500/20 flex items-center justify-center text-red-300 text-xs font-bold flex-shrink-0">
              {u.username?.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white text-sm font-medium">{u.username}</p>
              <p className="text-slate-500 text-xs">{u.department}</p>
            </div>
            <div className="text-right flex-shrink-0">
              <p className="text-white text-sm font-semibold">{u.avg_score?.toFixed(1)}</p>
              <RatingBadge rating={u.rating} />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}