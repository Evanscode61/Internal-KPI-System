import RatingBadge from '@/components/ui/RatingBadge'

export default function TopPerformers({ performers }) {
  return (
    <div className="bg-[#1a1d27] border border-white/10 rounded-2xl p-5 flex flex-col gap-4">
      <h2 className="text-white font-semibold text-sm">Top Performers</h2>

      {performers.length === 0 && (
        <p className="text-slate-600 text-sm italic">No data yet</p>
      )}

      {performers.map((p, idx) => (
        <div key={p.user_uuid} className="flex items-center gap-3">
          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0
            ${idx === 0 ? 'bg-amber-500/20 text-amber-400'  :
              idx === 1 ? 'bg-slate-400/20 text-slate-300'  :
              idx === 2 ? 'bg-orange-500/20 text-orange-400':
              'bg-white/5 text-slate-500'}`}
          >
            {idx + 1}
          </div>

          <div className="w-8 h-8 rounded-full bg-violet-500/20 flex items-center justify-center text-violet-300 text-xs font-bold flex-shrink-0">
            {p.username?.charAt(0).toUpperCase()}
          </div>

          <div className="flex-1 min-w-0">
            <p className="text-white text-sm font-medium truncate">{p.username}</p>
            <p className="text-slate-500 text-xs truncate">{p.department}</p>
          </div>

          <div className="text-right flex-shrink-0">
            <p className="text-white text-sm font-semibold">{p.avg_score?.toFixed(1)}</p>
            <RatingBadge rating={p.rating} />
          </div>
        </div>
      ))}
    </div>
  )
}