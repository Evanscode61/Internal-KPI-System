import React, { useState } from 'react'
import { useNotifications } from '../../hooks/useNotifications'
import { Button, PageHeader, ErrorMessage } from '../../components/ui'
import NotificationCard from '../../components/notifications/NotificationCard'

const FILTERS = ['All', 'Unread', 'KPI Alerts', 'Summaries']

const CheckAllIcon = () => (
  <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
  </svg>
)

export default function NotificationsPage() {
  const {
    notifications, unreadCount,
    isLoading, error, refetch,
    markRead, markAllRead, isMarkingAll,
    deleteNotification,
  } = useNotifications()

  const [filter, setFilter] = useState('All')

  const filtered = notifications.filter(n => {
    if (filter === 'Unread')     return !n.is_read
    if (filter === 'KPI Alerts') return n.notification_type === 'kpi_alert'
    if (filter === 'Summaries')  return n.notification_type === 'summary'
    return true
  })

  return (
    <div className="space-y-6 max-w-3xl">

      <PageHeader
        title="Notifications"
        subtitle={`${unreadCount} unread`}
        actions={
          unreadCount > 0 && (
            <Button variant="secondary" onClick={markAllRead} loading={isMarkingAll}>
              <CheckAllIcon /> Mark All Read
            </Button>
          )
        }
      />

      {/* ── Filter tabs */}
      <div className="flex items-center gap-2 flex-wrap">
        {FILTERS.map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all ${
              filter === f
                ? 'bg-brand-600/20 text-brand-400 border border-brand-500/20'
                : 'text-text-secondary hover:text-text-primary hover:bg-surface-muted border border-transparent'
            }`}
          >
            {f}
            {f === 'Unread' && unreadCount > 0 && (
              <span className="ml-1.5 bg-brand-500 text-white text-xs rounded-full px-1.5 py-0.5">
                {unreadCount}
              </span>
            )}
          </button>
        ))}
      </div>

      {error && <ErrorMessage message="Failed to load notifications" onRetry={refetch} />}

      {/* ── Notifications list */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="h-20 bg-surface-card rounded-xl border border-surface-border animate-pulse" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="w-16 h-16 rounded-2xl bg-surface-border flex items-center justify-center mb-4">
            <svg width="28" height="28" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24" className="text-text-muted">
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          </div>
          <p className="text-base font-semibold text-text-primary mb-1">No notifications</p>
          <p className="text-sm text-text-secondary">
            {filter === 'Unread' ? 'You are all caught up.' : 'Nothing to show here yet.'}
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {filtered.map(n => (
            <NotificationCard
              key={n.id}
              notification={n}
              onMarkRead={markRead}
              onDelete = {deleteNotification}
            />
          ))}
        </div>
      )}

    </div>
  )
}
