import React, { useState, useRef, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { useNotifications } from '../../hooks/useNotifications'

// ── Page title map
const PAGE_TITLES = {
  '/dashboard':       'Dashboard',
  '/notifications':   'Notifications',
  '/kpis':            'KPI Definitions',
  '/kpi-formulas':    'KPI Formulas',
  '/kpi-assignments': 'KPI Assignments',
  '/kpi-results':     'KPI Results',
  '/performance':     'Performance Summaries',
  '/users':           'Users',
  '/organization':    'Organization',
  '/audit':           'Audit Logs',
}

export default function Navbar() {
  const { user, logout }  = useAuth()
  const navigate          = useNavigate()
  const location          = useLocation()
  const { unreadCount }   = useNotifications()

  // ── Profile dropdown state
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef(null)

  const displayName = user?.username || 'User'
  const displayRole = user?.role     || ''
  const initial     = displayName.charAt(0).toUpperCase()
  const pageTitle   = PAGE_TITLES[location.pathname] || 'Dashboard'

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSignOut = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('kpi_user')
    if (logout) logout()
    navigate('/login')
  }

  return (
    <div className="h-16 bg-surface-card border-b border-surface-border flex items-center justify-between px-6">

      {/* Left — dynamic page title */}
      <h1 className="text-text-primary font-semibold text-lg">{pageTitle}</h1>

      {/* Right */}
      <div className="flex items-center gap-4">

        {/* Notification bell */}
        <button
          onClick={() => navigate('/notifications')}
          className="relative p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-surface-muted transition-colors"
          title="Notifications"
        >
          <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          {unreadCount > 0 && (
            <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </button>

        {/* Profile avatar with dropdown */}
        <div className="relative" ref={dropdownRef}>

          {/* Avatar button */}
          <div
            onClick={() => setDropdownOpen(prev => !prev)}
            className="flex items-center gap-2 cursor-pointer p-1.5 rounded-lg hover:bg-surface-muted transition-colors"
          >
            <div className="w-8 h-8 rounded-full bg-brand-600/20 border border-brand-500/30 flex items-center justify-center">
              <span className="text-xs font-bold text-brand-400">{initial}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-sm text-text-primary font-medium">{displayName}</span>
              {displayRole && <span className="text-xs text-text-secondary capitalize">{displayRole}</span>}
            </div>
            {/* Chevron */}
            <svg
              width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"
              className={`text-text-muted transition-transform ${dropdownOpen ? 'rotate-180' : ''}`}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
            </svg>
          </div>

          {/* Dropdown menu */}
          {dropdownOpen && (
            <div className="absolute right-0 top-12 w-52 bg-surface-card border border-surface-border rounded-xl shadow-lg z-50 overflow-hidden">

              {/* User info header */}
              <div className="px-4 py-3 border-b border-surface-border">
                <p className="text-sm font-medium text-text-primary">{displayName}</p>
                <p className="text-xs text-text-muted capitalize">{displayRole}</p>
              </div>

              {/* Menu items */}
              <div className="p-1">
                <button
                  onClick={() => { setDropdownOpen(false); navigate('/notifications') }}
                  className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-text-secondary hover:text-text-primary hover:bg-surface-muted transition-colors"
                >
                  <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                  </svg>
                  Notifications
                  {unreadCount > 0 && (
                    <span className="ml-auto bg-red-500 text-white text-[10px] font-bold rounded-full px-1.5 py-0.5">
                      {unreadCount}
                    </span>
                  )}
                </button>

                <button
                  onClick={() => { setDropdownOpen(false); navigate('/dashboard') }}
                  className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-text-secondary hover:text-text-primary hover:bg-surface-muted transition-colors"
                >
                  <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                  </svg>
                  Dashboard
                </button>
              </div>

              {/* Sign out */}
              <div className="p-1 border-t border-surface-border">
                <button
                  onClick={handleSignOut}
                  className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-red-400 hover:bg-red-500/10 transition-colors"
                >
                  <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  Sign Out
                </button>
              </div>

            </div>
          )}

        </div>

      </div>
    </div>
  )
}