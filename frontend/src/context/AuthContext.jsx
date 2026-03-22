import React, { createContext, useContext, useState, useEffect } from 'react'
import axiosInstance, { setAuthToken, clearAuthToken } from '@/api/axiosInstance'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null)
  const [loading, setLoading] = useState(true)

 // On app load — restore token from localStorage if it exists
useEffect(() => {
  const token = localStorage.getItem('access_token')
  if (token) {
    setAuthToken(token)
    // decode user info directly from the JWT payload
    try {
      const payload  = JSON.parse(atob(token.split('.')[1]))
      const userData = {
        id:       payload.user_id,
        username: payload.username,
        role:     payload.role,
      }
      setUser(userData)
      localStorage.setItem('kpi_user', JSON.stringify(userData))
    } catch (e) {
      console.error('Failed to decode token', e)
    }
  }
  setLoading(false)
}, [])

  const login = async (username, password) => {
    const res = await axiosInstance.post('/auth/login/', { username, password })
    const { access_token, refresh_token } = res.data.data

    // Save tokens
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', refresh_token)

    // Decode user info from JWT payload
    const payload = JSON.parse(atob(access_token.split('.')[1]))
    const userData = {
      id:       payload.user_id,
      username: payload.username,
      role:     payload.role,
    }

    localStorage.setItem('kpi_user', JSON.stringify(userData))
    setAuthToken(access_token)
    setUser(userData)
    return userData
  }

  const logout = () => {
    const refresh_token = localStorage.getItem('refresh_token')
    if (refresh_token) {
      axiosInstance.post('/auth/logout/', { refresh_token }).catch(() => {})
    }
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('kpi_user')
    clearAuthToken()
    setUser(null)
  }

  const hasRole       = (role) => user?.role === role
  const isAdmin       = () => user?.role === 'admin'
  const isHR          = () => user?.role === 'hr'
  const isManager     = () => ['Business_Line_Manager', 'Tech_Line_Manager'].includes(user?.role)
  const isEmployee    = () => user?.role === 'employee'
  const canManageKPIs = () => isAdmin() || isHR() || isManager()

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      login,
      logout,
      hasRole,
      isAdmin,
      isHR,
      isManager,
      isEmployee,
      canManageKPIs,
      isAuthenticated: !!user,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}