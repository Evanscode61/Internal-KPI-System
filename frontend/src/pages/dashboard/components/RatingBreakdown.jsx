const RATING_CONFIG = {
  outstanding:       { color: 'bg-emerald-500', label: 'Outstanding' },
  good:              { color: 'bg-blue-500',     label: 'Good' },
  satisfactory:      { color: 'bg-violet-500',   label: 'Satisfactory' },
  needs_improvement: { color: 'bg-amber-500',    label: 'Needs Improvement' },
  poor:              { color: 'bg-red-500',       label: 'Poor' },
}

export default function RatingBreakdown({ ratings }) {
  const total = Object.values(ratings).reduce((a, b) => a + b, 0)

  return (
    <div className="bg-[#1a1d27] border border-white/10 rounded-2xl p-5 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-white font-semibold text-sm">Rating Breakdown</h2>
        <span className="text-slate-500 text-xs">{total} total results</span>
      </div>

      {total === 0 ? (
        <p className="text-slate-600 text-sm italic">No results yet</p>
      ) : (
        <>
          <div className="flex h-3 rounded-full overflow-hidden gap-0.5">
            {Object.entries(ratings).map(([key, count]) => {
              const pct = total > 0 ? (count / total) * 100 : 0
              const cfg = RATING_CONFIG[key]
              return pct > 0 ? (
                <div
                  key={key}
                  className={`${cfg.color} h-full`}
                  style={{ width: `${pct}%` }}
                  title={`${cfg.label}: ${count}`}
                />
              ) : null
            })}
          </div>

          <div className="flex flex-wrap gap-4">
            {Object.entries(ratings).map(([key, count]) => {
              const cfg = RATING_CONFIG[key]
              const pct = total > 0 ? Math.round((count / total) * 100) : 0
              return (
                <div key={key} className="flex items-center gap-2">
                  <div className={`w-2.5 h-2.5 rounded-full ${cfg.color}`} />
                  <span className="text-slate-400 text-xs">{cfg.label}</span>
                  <span className="text-white text-xs font-semibold">{count}</span>
                  <span className="text-slate-600 text-xs">({pct}%)</span>
                </div>
              )
            })}
          </div>
        </>
      )}
    </div>
  )
}