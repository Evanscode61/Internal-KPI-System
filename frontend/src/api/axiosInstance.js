import axios from 'axios'
import toast from 'react-hot-toast'

const BASE_URL = import.meta.env.VITE_API_URL || '/api'

const axiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

let _accessToken = null
let _isRefreshing = false
let _failedQueue = []

function processQueue(error, token = null) {
  _failedQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error)
    else resolve(token)
  })
  _failedQueue = []
}

export function setAuthToken(token) {
  _accessToken = token
  axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

export function clearAuthToken() {
  _accessToken = null
  delete axiosInstance.defaults.headers.common['Authorization']
}

axiosInstance.interceptors.request.use(
  (config) => {
    // Use in-memory token first, fall back to localStorage
    const token = _accessToken || localStorage.getItem('access_token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (_isRefreshing) {
        return new Promise((resolve, reject) => {
          _failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            originalRequest.headers['Authorization'] = `Bearer ${token}`
            return axiosInstance(originalRequest)
          })
          .catch((err) => Promise.reject(err))
      }

      originalRequest._retry = true
      _isRefreshing = true

      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        _isRefreshing = false
        window.dispatchEvent(new CustomEvent('auth:logout'))
        return Promise.reject(error)
      }

      try {
        const { data } = await axios.post(`${BASE_URL}/auth/refresh/`, {
          refresh_token: refreshToken,
        })
        const newToken = data.data.access_token
        setAuthToken(newToken)
        processQueue(null, newToken)
        originalRequest.headers['Authorization'] = `Bearer ${newToken}`
        return axiosInstance(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('kpi_user')
        clearAuthToken()
        window.dispatchEvent(new CustomEvent('auth:logout'))
        return Promise.reject(refreshError)
      } finally {
        _isRefreshing = false
      }
    }

    if (error.response?.status !== 401) {
      const message =
        error.response?.data?.error ||
        error.response?.data?.message ||
        error.message ||
        'An unexpected error occurred'
      if (error.response?.status >= 500) {
        toast.error(`Server error: ${message}`)
      }
    }

    return Promise.reject(error)
  }
)

export default axiosInstance


