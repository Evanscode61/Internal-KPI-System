import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-surface-DEFAULT">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-brand-600 flex items-center justify-center">
            <svg className="w-5 h-5 text-white animate-pulse" fill="currentColor" viewBox="0 0 24 24">
              <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <p className="text-text-secondary text-sm">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return children
}

export function RoleBasedRoute({ children, roles }) {
  const { hasRole } = useAuth()

if (roles && roles.length > 0 && !roles.some(r => hasRole(r))) {
    return <Navigate to="/dashboard" replace />
  }

  return children
}