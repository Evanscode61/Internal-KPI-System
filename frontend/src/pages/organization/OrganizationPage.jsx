import { useState, useEffect } from 'react'
import Toast from '@/components/ui/Toast'
import DepartmentsTab from './DepartmentsTab'
import TeamsTab from './TeamsTab'
import { getDepartments, getTeams } from '@/services/orgService'

export default function OrganizationPage() {
  const [depts, setDepts]         = useState([])
  const [teams, setTeams]         = useState([])
  const [loading, setLoading]     = useState(true)
  const [error, setError]         = useState('')
  const [activeTab, setActiveTab] = useState('departments')
  const [successMsg, setSuccessMsg] = useState('')

  const fetchAll = () => {
    setLoading(true)
    Promise.all([getDepartments(), getTeams()])
      .then(([d, t]) => {
        setDepts(d.data?.data || [])
        setTeams(t.data?.data || [])
      })
      .catch(() => setError('Failed to load organization data'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchAll() }, [])

  const showSuccess = (msg) => {
    setSuccessMsg(msg)
    setTimeout(() => setSuccessMsg(''), 3000)
  }

  return (
    <div className="p-6 flex flex-col gap-6">
      <Toast message={successMsg} />

      {/* Header */}
      <div>
        <h1 className="text-white text-xl font-semibold tracking-tight">Organization</h1>
        <p className="text-slate-500 text-sm mt-1">Manage departments and teams</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-[#1a1d27] border border-white/10 rounded-xl p-1 w-fit">
        {['departments', 'teams'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-5 py-2 rounded-lg text-sm font-medium transition-colors capitalize
              ${activeTab === tab ? 'bg-violet-600 text-white' : 'text-slate-400 hover:text-white'}`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="w-6 h-6 border-2 border-violet-500/30 border-t-violet-500 rounded-full animate-spin" />
        </div>
      )}

      {/* Error */}
      {!loading && error && (
        <div className="flex items-center justify-center py-20">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      {/* Content */}
      {!loading && !error && activeTab === 'departments' && (
        <DepartmentsTab depts={depts} onRefresh={fetchAll} showSuccess={showSuccess} />
      )}

      {!loading && !error && activeTab === 'teams' && (
        <TeamsTab teams={teams} depts={depts} onRefresh={fetchAll} showSuccess={showSuccess} />
      )}
    </div>
  )
}
