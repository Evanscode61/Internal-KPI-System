import { useState, useEffect } from 'react'
import CompanyDashboard  from './CompanyDashboard'
import ManagerDashboard  from './ManagerDashboard'
import EmployeeDashboard from './EmployeeDashboard'
import { getDashboard }  from '@/services/dashboardService'
import { alertsApi }     from '@/api'

// ── Period presets
const PERIOD_PRESETS = [
  { label: 'All Time',   start: '',       end: ''       },
  { label: 'This Month', start: 'month',  end: 'month'  },
  { label: 'Q1',         start: '-01-01', end: '-03-31' },
  { label: 'Q2',         start: '-04-01', end: '-06-30' },
  { label: 'Q3',         start: '-07-01', end: '-09-30' },
  { label: 'Q4',         start: '-10-01', end: '-12-31' },
]

function thisMonth() {
  const now   = new Date()
  const year  = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const last  = new Date(year, now.getMonth() + 1, 0).getDate()
  return { start: `${year}-${month}-01`, end: `${year}-${month}-${last}` }
}

function getPresetDates(preset) {
  if (!preset.start) return { start: '', end: '' }
  if (preset.start === 'month') return thisMonth()
  const year = new Date().getFullYear()
  return {
    start: `${year}${preset.start}`,
    end:   `${year}${preset.end}`,
  }
}

export default function DashboardPage() {
  const [data,         setData]         = useState(null)
  const [alerts,       setAlerts]       = useState([])
  const [loading,      setLoading]      = useState(true)
  const [error,        setError]        = useState('')
  const [activePreset, setActivePreset] = useState('All Time')
  const [customStart,  setCustomStart]  = useState('')
  const [customEnd,    setCustomEnd]    = useState('')

  // ── Fetch dashboard data
  const fetchDashboard = (start = '', end = '') => {
    setLoading(true)
    setError('')
    const params = new URLSearchParams()
    if (start) params.append('period_start', start)
    if (end)   params.append('period_end',   end)
    getDashboard(params.toString())
      .then(res => setData(res.data?.data))
      .catch(() => setError('Failed to load dashboard'))
      .finally(() => setLoading(false))
  }

  // ── Fetch alerts silently
  const fetchAlerts = async () => {
    try {
      const res = await alertsApi.getAll()
      setAlerts(res.data?.data ?? [])
    } catch {
      // silently fail — alerts are not critical
    }
  }

  useEffect(() => {
    fetchDashboard()
    fetchAlerts()
  }, [])

  // ── Period preset handler
  const handlePreset = (preset) => {
    setActivePreset(preset.label)
    const { start, end } = getPresetDates(preset)
    fetchDashboard(start, end)
  }

  // ── Custom range handler
  const handleCustom = () => {
    if (!customStart || !customEnd) return
    setActivePreset('Custom')
    fetchDashboard(customStart, customEnd)
  }

  const subtitle = {
    company:    `Company performance overview — ${data?.period}`,
    department: `${data?.department} department — ${data?.period}`,
    employee:   `${data?.username} · ${data?.team} · ${data?.period}`,
  }[data?.scope] || data?.period

  return (
    <div className="flex flex-col gap-6">

      {/* ── Header + Period filter */}
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-white text-xl font-semibold tracking-tight">Dashboard</h1>
          {data && <p className="text-slate-500 text-sm mt-1">{subtitle}</p>}
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          {/* Preset buttons */}
          {PERIOD_PRESETS.map(preset => (
            <button
              key={preset.label}
              onClick={() => handlePreset(preset)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activePreset === preset.label
                  ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                  : 'text-slate-400 hover:text-white hover:bg-white/5 border border-transparent'
              }`}
            >
              {preset.label}
            </button>
          ))}

          {/* Custom range */}
          <div className="flex items-center gap-1.5">
            <input
              type="date"
              value={customStart}
              onChange={e => setCustomStart(e.target.value)}
              className="bg-[#1a1d27] border border-white/10 text-slate-300 text-xs rounded-lg px-2 py-1.5 outline-none focus:border-violet-500/50"
            />
            <span className="text-slate-600 text-xs">→</span>
            <input
              type="date"
              value={customEnd}
              onChange={e => setCustomEnd(e.target.value)}
              className="bg-[#1a1d27] border border-white/10 text-slate-300 text-xs rounded-lg px-2 py-1.5 outline-none focus:border-violet-500/50"
            />
            <button
              onClick={handleCustom}
              className="px-3 py-1.5 rounded-lg text-xs font-medium bg-violet-500/20 text-violet-300 border border-violet-500/30 hover:bg-violet-500/30 transition-all"
            >
              Apply
            </button>
          </div>
        </div>
      </div>

      {/* ── Loading */}
      {loading && (
        <div className="flex items-center justify-center h-64">
          <div className="w-6 h-6 border-2 border-violet-500/30 border-t-violet-500 rounded-full animate-spin" />
        </div>
      )}

      {/* ── Error */}
      {error && !loading && (
        <div className="flex items-center justify-center h-64">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      {/* ── Dashboard content */}
      {!loading && !error && data && (
        <>
          {data.scope === 'employee' && (
            <EmployeeDashboard data={data} />
          )}
          {data.scope === 'department' && (
            <ManagerDashboard
              data={data}
              alerts={alerts}
              onAlertResolved={fetchAlerts}
            />
          )}
          {data.scope === 'company' && (
            <CompanyDashboard
              data={data}
              alerts={alerts}
              onAlertResolved={fetchAlerts}
            />
          )}
        </>
      )}

    </div>
  )
}