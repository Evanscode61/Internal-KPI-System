import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

function NavItem({ to, icon, label }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        isActive
          ? 'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium bg-brand-600/20 text-brand-400 border border-brand-500/20 cursor-pointer mb-0.5'
          : 'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-text-secondary hover:text-text-primary hover:bg-surface-muted cursor-pointer mb-0.5'
      }
    >
      {icon}
      {label}
    </NavLink>
  )
}

export default function Sidebar() {
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const role     = user?.role || ""
  const isAdmin  = role === "admin"
  const isHR     = role === "hr"
  const isManager = role === "Business_Line_Manager" || role === "Tech_Line_Manager"

  const handleSignOut = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('kpi_user')
    if (logout) logout()
    navigate('/login')
  }

  return (
    <aside className="w-60 h-screen bg-surface-card border-r border-surface-border flex flex-col flex-shrink-0">

      {/* Logo */}
      <div className="px-4 py-5 border-b border-surface-border flex items-center gap-3">
        <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center flex-shrink-0">
          <span className="text-white text-sm font-bold">K</span>
        </div>
        <div>
          <p className="text-text-primary text-sm font-bold leading-none">KPI Manager</p>
          <p className="text-text-muted text-[10px] mt-0.5 capitalize">{role || "—"}</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 sidebar-scroll">

        {/* Overview — everyone */}
        <p className="text-text-muted text-[10px] font-semibold uppercase tracking-widest px-3 mb-1">
          Overview
        </p>

        <NavItem to="/dashboard" label="Dashboard" icon={
          <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
        } />

        <NavItem to="/notifications" label="Notifications" icon={
          <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
        } />

        {/* KPIs — everyone */}
        <p className="text-text-muted text-[10px] font-semibold uppercase tracking-widest px-3 mb-1 mt-4">
          KPIs
        </p>

        {/* KPI Definitions — admin, hr, managers only */}
        {(isAdmin || isHR || isManager) && (
          <NavItem to="/kpis" label="KPI Definitions" icon={
            <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          } />
        )}
        {/* KPI Formulas — managers only */}
{(isManager || isAdmin) && (
  <NavItem to="/kpi-formulas" label="KPI Formulas" icon={
    <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 11h.01M12 11h.01M15 11h.01M4 19h16a2 2 0 002-2V7a2 2 0 00-2-2H4a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
  } />
)}
        

        {/* Assignments — everyone */}
        <NavItem to="/kpi-assignments" label="KPI Assignments" icon={
          <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
        } />

        {/* Results — everyone */}
        <NavItem to="/kpi-results" label="KPI Results" icon={
          <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        } />

        {/* Performance viewed by everyone */}
        <p className="text-text-muted text-[10px] font-semibold uppercase tracking-widest px-3 mb-1 mt-4">
          Performance
        </p>

        <NavItem to="/performance" label="Performance Summaries" icon={
          <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        } />

        {/* Administration viewed by admin and hr only */}
        {(isAdmin || isHR) && (
          <>
            <p className="text-text-muted text-[10px] font-semibold uppercase tracking-widest px-3 mb-1 mt-4">
              Administration
            </p>

            <NavItem to="/users" label="Users" icon={
              <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            } />

            <NavItem to="/organization" label="Organization" icon={
              <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            } />

            {/* Audit Logs, viewed by  admin only */}
            {isAdmin && (
              <NavItem to="/audit" label="Audit Logs" icon={
                <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              } />
            )}
          </>
        )}

      </nav>

      {/* User Footer */}
      <div className="px-3 py-4 border-t border-surface-border">
        <div className="flex items-center gap-3 px-2 py-2 mb-2">
          <div className="w-8 h-8 rounded-full bg-brand-600/20 border border-brand-500/30 flex items-center justify-center flex-shrink-0">
            <span className="text-xs font-bold text-brand-400">
              {user?.username?.charAt(0).toUpperCase() || "?"}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-text-primary truncate">{user?.username || "—"}</p>
            <p className="text-[10px] text-text-muted truncate capitalize">{role || "—"}</p>
          </div>
        </div>

        <div
          onClick={handleSignOut}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-text-secondary hover:text-red-400 hover:bg-red-500/10 cursor-pointer transition-colors"
        >
          <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          Sign Out
        </div>
      </div>

    </aside>
  )
}