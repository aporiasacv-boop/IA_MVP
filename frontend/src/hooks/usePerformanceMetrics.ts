import { useCallback, useEffect, useState } from 'react'
import { loadLivePerformanceRecords } from '../services/performanceApi'
import {
  aggregateRecords,
  getPerformanceRecords,
  pickSavingsExample,
} from '../services/performanceStore'
import type { PerformanceMetrics, SavingsExample } from '../types/performance'

export function usePerformanceMetrics() {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null)
  const [savingsExample, setSavingsExample] = useState<SavingsExample | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      const sessionRecords = getPerformanceRecords()
      const records = await loadLivePerformanceRecords(sessionRecords)
      setMetrics(aggregateRecords(records))
      setSavingsExample(pickSavingsExample(records))
    } catch {
      setError('No fue posible obtener métricas de rendimiento del sistema.')
      const sessionOnly = getPerformanceRecords()
      if (sessionOnly.length > 0) {
        setMetrics(aggregateRecords(sessionOnly))
        setSavingsExample(pickSavingsExample(sessionOnly))
      }
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  return { metrics, savingsExample, isLoading, error, refresh }
}
