import { useRef } from 'react'
import RatingBadge from '@/components/ui/RatingBadge'
import StatCards from './components/StatCards'
import RatingBreakdown from './components/RatingBreakdown'
import TopPerformers from './components/TopPerformers'
import NeedsAttention from './components/NeedsAttention'
import AlertsPanel from './components/AlertsPanel'
import HealthScore from './components/HealthScore'

export default function CompanyDashboard({ data, alerts, onAlertResolved }) {
  const overview  = data?.company_overview || {}
  const alertsRef = useRef(null)

  const handleAlertsClick = () => {
    alertsRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const stats = [
    { label: 'KPIs Assigned',     value: overview?.total_kpis_assigned           ?? '—', icon: '📋', color: 'text-violet-400',  bg: 'bg-violet-500/10',  href: '/kpi-assignments'              },
    { label: 'Results Submitted', value: overview?.total_results_submitted        ?? '—', icon: '✅', color: 'text-emerald-400', bg: 'bg-emerald-500/10', href: '/kpi-results'                  },
    { label: 'Submission Rate',   value: overview?.submission_rate                ?? '—', icon: '📈', color: 'text-blue-400',    bg: 'bg-blue-500/10',    href: '/kpi-results'                  },
    { label: 'Active Alerts',     value: data?.alerts_summary?.total_active_alerts ?? '—', icon: '🔔', color: 'text-amber-400',  bg: 'bg-amber-500/10',   onClick: handleAlertsClick            },
  ]

  return (
    <>
      {/* ── Company Health Score */}
      <HealthScore
        score        = {overview?.average_score}
        resultCount  = {overview?.total_results_submitted}
        lastDataDate = {data?.period}
        title        = "Company Health Score"
      />

      <StatCards stats={stats} />
      <RatingBreakdown ratings={overview?.rating_breakdown || {}} />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-[#1a1d27] border border-white/10 rounded-2xl p-5 flex flex-col gap-4">
          <h2 className="text-white font-semibold text-sm">Departments</h2>
          {(data?.departments || []).length === 0 && (
            <p className="text-slate-600 text-sm italic">No department data</p>
          )}
          {(data?.departments || []).map(dept => (
            <div key={dept.department_uuid} className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span className="text-white text-sm font-medium">{dept.name}</span>
                <div className="flex items-center gap-2">
                  {dept.weighted_score !== null && (
                    <span className="text-slate-400 text-xs">{dept.weighted_score}%</span>
                  )}
                  <RatingBadge rating={dept.rating} />
                </div>
              </div>
              <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                <div
                  className="h-full bg-violet-500 rounded-full"
                  style={{ width: dept.weighted_score ? `${Math.min(dept.weighted_score, 100)}%` : '0%' }}
                />
              </div>
              <div className="flex flex-col gap-1 pl-3 border-l border-white/10">
                {dept.teams.map(team => (
                  <div key={team.team_uuid} className="flex items-center justify-between py-1">
                    <span className="text-slate-400 text-xs">{team.name}</span>
                    <div className="flex items-center gap-2">
                      {team.weighted_score !== null && (
                        <span className="text-slate-500 text-xs">{team.weighted_score}%</span>
                      )}
                      <RatingBadge rating={team.rating} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
        <TopPerformers performers={data?.top_performers || []} />
      </div>

      <NeedsAttention users={data?.needs_attention} />

      {/* ── Alerts Panel */}
      <div ref={alertsRef}>
        <AlertsPanel alerts={alerts} onResolved={onAlertResolved} />
      </div>
    </>
  )
}