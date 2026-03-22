function getHealthConfig(score) {
  if (!score || isNaN(score)) return { color: '#94a3b8', bg: 'rgba(148,163,184,0.1)', border: 'rgba(148,163,184,0.2)', label: 'No Data' }
  if (score >= 85) return { color: '#4ade80', bg: 'rgba(34,197,94,0.1)',   border: 'rgba(34,197,94,0.2)',   label: 'Excellent'        }
  if (score >= 70) return { color: '#818cf8', bg: 'rgba(129,140,248,0.1)', border: 'rgba(129,140,248,0.2)', label: 'Good'             }
  if (score >= 50) return { color: '#fb923c', bg: 'rgba(251,146,60,0.1)',  border: 'rgba(251,146,60,0.2)',  label: 'Needs Attention'  }
  return             { color: '#f87171', bg: 'rgba(239,68,68,0.1)',    border: 'rgba(239,68,68,0.2)',   label: 'Critical'         }
}

export default function HealthScore({ score, resultCount, lastDataDate, title = 'Health Score' }) {
  const s       = parseFloat(score) || 0
  const config  = getHealthConfig(s)

  return (
    <div
      className="bg-[#1a1d27] rounded-2xl p-6 flex flex-col gap-4"
      style={{ border: `1px solid ${config.border}` }}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-slate-500 text-xs uppercase tracking-wide font-medium">{title}</p>
          <div className="flex items-end gap-3 mt-2">
            <p className="text-5xl font-bold" style={{ color: config.color }}>
              {score ? `${parseFloat(score).toFixed(1)}%` : '—'}
            </p>
            <span
              className="text-sm font-semibold px-3 py-1 rounded-full mb-1"
              style={{ color: config.color, background: config.bg }}
            >
              {config.label}
            </span>
          </div>
        </div>

        {/* Progress ring */}
        <div className="relative w-16 h-16 flex-shrink-0">
          <svg viewBox="0 0 36 36" className="w-full h-full -rotate-90">
            <circle cx="18" cy="18" r="15.9" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="3" />
            <circle
              cx="18" cy="18" r="15.9" fill="none"
              stroke={config.color}
              strokeWidth="3"
              strokeDasharray={`${Math.min(s, 100)} 100`}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-xs font-bold" style={{ color: config.color }}>
              {score ? `${Math.round(s)}%` : '—'}
            </span>
          </div>
        </div>
      </div>

      {/* Progress bar */}
      <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${Math.min(s, 100)}%`, backgroundColor: config.color }}
        />
      </div>

      {/* Footer info */}
      <div className="flex items-center justify-between text-xs text-slate-500">
        <span>
          {resultCount ? `Based on ${resultCount} approved results` : 'No results yet'}
        </span>
        {lastDataDate && (
          <span>Last data: {lastDataDate}</span>
        )}
      </div>
    </div>
  )
}