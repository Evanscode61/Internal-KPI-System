import { useState, useEffect, useCallback, useRef } from 'react'

export function useApi(apiFn, deps = [], immediate = true) {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(immediate)
  const [error, setError]     = useState(null)
  const mountedRef            = useRef(true)

  useEffect(() => {
    mountedRef.current = true
    return () => { mountedRef.current = false }
  }, [])

  const execute = useCallback(async (...args) => {
    setLoading(true)
    setError(null)
    try {
      const res = await apiFn(...args)
      if (mountedRef.current) {
        setData(res.data?.data ?? res.data)
      }
      return res.data?.data ?? res.data
    } catch (err) {
      const msg = err.response?.data?.error || err.response?.data?.message || err.message || 'Request failed'
      if (mountedRef.current) setError(msg)
      throw err
    } finally {
      if (mountedRef.current) setLoading(false)
    }
  }, [apiFn])

  useEffect(() => {
    if (immediate) execute()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  const refresh = () => execute()

  return { data, loading, error, execute, refresh }
}

export function useMutation(apiFn) {
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  const mutate = useCallback(async (...args) => {
    setLoading(true)
    setError(null)
    try {
      const res = await apiFn(...args)
      return res.data?.data ?? res.data
    } catch (err) {
      const msg = err.response?.data?.error || err.response?.data?.message || err.message || 'Request failed'
      setError(msg)
      throw err
    } finally {
      setLoading(false)
    }
  }, [apiFn])

  return { mutate, loading, error }
}