import React from 'react'
import { useNavigate } from 'react-router-dom'

const typeLabels = {
  kpi_alert: 'KPI Alert',
  summary:   'Performance Summary',
}
const TrashIcon = () => (
  <svg width="13" height="13" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
  </svg>
)

const typeIcons = {
  kpi_alert: (
    <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  ),
  summary: (
    <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  ),
}

function timeAgo(dateStr) {
  const diff  = Date.now() - new Date(dateStr).getTime()
  const mins  = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days  = Math.floor(diff / 86400000)
  if (mins < 1)   return 'Just now'
  if (mins < 60)  return `${mins}m ago`
  if (hours < 24) return `${hours}h ago`
  return `${days}d ago`
}

export default function NotificationCard({ notification, onMarkRead, onDelete }) {
  const navigate = useNavigate()
  const isUnread = !notification.is_read

  const handleClick = () => {
    if (isUnread) onMarkRead(notification.id)
    if (notification.notification_type === 'kpi_alert') navigate('/kpi-results')
    if (notification.notification_type === 'summary')   navigate('/performance')
  }

  return (
    <div
      onClick={handleClick}
      className={`
        flex items-start gap-4 p-4 rounded-xl border cursor-pointer transition-all duration-200
        ${isUnread
          ? 'bg-surface-card border-surface-border hover:bg-surface-muted'
          : 'bg-transparent border-transparent hover:bg-surface-muted opacity-50 hover:opacity-80'
        }
      `}
    >
      {/* Icon — brand color for all */}
      <div className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5 bg-brand-600/10 text-brand-400 border border-brand-500/20">
        {typeIcons[notification.notification_type] || typeIcons.kpi_alert}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-semibold text-brand-400">
            {typeLabels[notification.notification_type] || notification.notification_type}
          </span>
          {notification.kpi_name && (
            <span className="text-xs text-text-muted truncate">· {notification.kpi_name}</span>
          )}
          {isUnread && (
            <span className="w-2 h-2 rounded-full bg-brand-500 flex-shrink-0 ml-auto" />
          )}
        </div>
        <p className="text-sm text-text-primary leading-snug">{notification.message}</p>
        <p className="text-xs text-text-muted mt-1">{timeAgo(notification.created_at)}</p>
        {/* Delete button */}
<button
  onClick={(e) => { e.stopPropagation(); onDelete(notification.id) }}
  className="p-1.5 rounded-lg text-text-muted hover:text-red-400 hover:bg-red-500/10 transition-colors flex-shrink-0 self-center"
  title="Delete notification"
>
  <TrashIcon />
</button>
      </div> 
    </div>
  )
}