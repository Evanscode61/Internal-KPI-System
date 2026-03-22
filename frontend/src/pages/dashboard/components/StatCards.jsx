import { useNavigate } from 'react-router-dom'

export default function StatCards({ stats = [] }) {
  const navigate = useNavigate()

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {stats.map(stat => (
        <div
          key={stat.label}
          onClick={() => {
            if (stat.href) navigate(stat.href)
            if (stat.onClick) stat.onClick()
          }}
          className={`bg-[#1a1d27] border border-white/10 rounded-2xl p-5 flex flex-col gap-3
            ${stat.href || stat.onClick ? 'cursor-pointer hover:border-white/20 hover:bg-white/[0.03] transition-all' : ''}`}
        >
          <div className={`w-9 h-9 rounded-xl ${stat.bg} flex items-center justify-center text-lg`}>
            {stat.icon}
          </div>
          <div>
            <p className="text-slate-500 text-xs uppercase tracking-wide font-medium mb-1">
              {stat.label}
            </p>
            <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
            {stat.subtitle && (
              <p className="text-slate-600 text-xs mt-1">{stat.subtitle}</p>
            )}
          </div>
          {(stat.href || stat.onClick) && (
            <p className="text-slate-600 text-xs mt-auto">Click to view →</p>
          )}
        </div>
      ))}
    </div>
  )
}