import RatingBadge from '@/components/ui/RatingBadge'
import StatCards from './components/StatCards'
import RatingBreakdown from './components/RatingBreakdown'

export default function EmployeeDashboard({ data }) {
  const stats = [
    { label: 'KPIs Assigned',   value: data?.kpis_assigned       ?? '—', icon: '📋', color: 'text-violet-400',  bg: 'bg-violet-500/10',  href: '/kpi-assignments' },
    { label: 'KPIs Submitted',  value: data?.kpis_submitted       ?? '—', icon: '✅', color: 'text-emerald-400', bg: 'bg-emerald-500/10', href: '/kpi-results'     },
    { label: 'Submission Rate', value: data?.submission_rate      ?? '—', icon: '📈', color: 'text-blue-400',    bg: 'bg-blue-500/10',    href: '/kpi-results'     },
    { label: 'Notifications',   value: data?.unread_notifications ?? '—', icon: '🔔', color: 'text-amber-400',   bg: 'bg-amber-500/10',   href: '/notifications'   },
  ]

  return (
    <>
      <StatCards stats={stats} />
      <RatingBreakdown ratings={data?.rating_breakdown || {}} />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

        {/* Recent Results */}
        <div className="bg-[#1a1d27] border border-white/10 rounded-2xl p-5 flex flex-col gap-4">
          <h2 className="text-white font-semibold text-sm">Recent Results</h2>
          {(data?.recent_results || []).length === 0 && (
            <p className="text-slate-600 text-sm italic">No results yet</p>
          )}
          {(data?.recent_results || []).map((r, idx) => (
            <div key={idx} className="flex items-center justify-between py-2 border-b border-white/[0.06] last:border-0">
              <div>
                <p className="text-white text-sm font-medium">{r.kpi_name}</p>
                <p className="text-slate-500 text-xs mt-0.5">
                  {new Date(r.submitted_at).toLocaleDateString()}
                </p>
              </div>
              <div className="text-right">
                <p className="text-white text-sm font-semibold">{parseFloat(r.calculated_score).toFixed(1)}</p>
                <RatingBadge rating={r.rating} />
              </div>
            </div>
          ))}
        </div>

        {/* Performance Summaries */}
        <div className="bg-[#1a1d27] border border-white/10 rounded-2xl p-5 flex flex-col gap-4">
          <h2 className="text-white font-semibold text-sm">Performance Summaries</h2>
          {(data?.performance_summaries || []).length === 0 && (
            <p className="text-slate-600 text-sm italic">No summaries yet</p>
          )}
          {(data?.performance_summaries || []).map((s, idx) => (
            <div key={idx} className="flex items-center justify-between py-2 border-b border-white/[0.06] last:border-0">
              <p className="text-slate-400 text-sm">{s.period}</p>
              <p className="text-white text-sm font-semibold">{parseFloat(s.weighted_score).toFixed(1)}%</p>
            </div>
          ))}
        </div>

      </div>
    </>
  )
}