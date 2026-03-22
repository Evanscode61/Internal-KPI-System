import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { notificationsApi } from '../api'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

export function useNotifications() {
  const { loading: authLoading } = useAuth()
  const queryClient = useQueryClient()

  const { data: allData, isLoading, error, refetch } = useQuery({
    queryKey: ['notifications'],
    queryFn:  () => notificationsApi.getAll().then(r => r.data?.data ?? []),
    enabled:  !authLoading,
  })

  const { data: unreadData } = useQuery({
    queryKey: ['notifications-unread'],
    queryFn:  () => notificationsApi.getUnread().then(r => r.data?.data ?? []),
    enabled:  !authLoading,
    refetchInterval: 60000, // poll every 60 seconds
  })

  const markReadMutation = useMutation({
    mutationFn: (id) => notificationsApi.markRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      queryClient.invalidateQueries({ queryKey: ['notifications-unread'] })
    },
    onError: () => toast.error('Failed to mark as read'),
  })

  const markAllReadMutation = useMutation({
    mutationFn: () => notificationsApi.markAllRead(),
    onSuccess: () => {
      toast.success('All notifications marked as read')
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      queryClient.invalidateQueries({ queryKey: ['notifications-unread'] })
    },
    onError: () => toast.error('Failed to mark all as read'),
  })

  const deleteMutation = useMutation({
  mutationFn: (id) => notificationsApi.delete(id),
  onSuccess: () => {
    toast.success('Notification deleted')
    queryClient.invalidateQueries({ queryKey: ['notifications'] })
    queryClient.invalidateQueries({ queryKey: ['notifications-unread'] })
  },
  onError: () => toast.error('Failed to delete notification'),
})
  const notifications  = Array.isArray(allData)    ? allData    : []
  const unreadCount    = Array.isArray(unreadData)  ? unreadData.length : 0

  return {
    notifications,
    unreadCount,
    isLoading,
    error,
    refetch,
    markRead:    (id) => markReadMutation.mutate(id),
    markAllRead: ()   => markAllReadMutation.mutate(),
    isMarkingAll: markAllReadMutation.isPending,
    deleteNotification: (id) => deleteMutation.mutate(id),
  }
}