import { useCallback, useEffect, useState } from 'react'
import * as metricsApi from '../services/metricsApi'
import type { MetricsSummary, PerformanceStats, TopQueryItem } from '../types/metrics'

export interface BackendMetricsData {
  summary: MetricsSummary
  performance: PerformanceStats
  topQueries: TopQueryItem[]
}

export function useBackendMetrics() {
  const [data, setData] = useState<BackendMetricsData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      const [summary, performance, topQueries] = await Promise.all([
        metricsApi.getSummary(),
        metricsApi.getPerformance(),
        metricsApi.getTopQueries(10),
      ])
      setData({ summary, performance, topQueries })
    } catch {
      setError('No fue posible obtener métricas reales del backend.')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  return { data, isLoading, error, refresh }
}
