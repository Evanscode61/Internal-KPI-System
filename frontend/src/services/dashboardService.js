import axiosInstance from '@/api/axiosInstance'

export const getDashboard = (params = '') =>
  axiosInstance.get(`/performance/dashboard/${params ? '?' + params : ''}`)