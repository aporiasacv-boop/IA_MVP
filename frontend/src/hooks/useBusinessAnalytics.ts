import { useCallback, useEffect, useState } from 'react'
import * as businessAnalyticsApi from '../services/businessAnalyticsApi'
import type { BusinessAnalyticsData } from '../types/businessAnalytics'
import { es } from '../i18n/spanish'

export function useBusinessAnalytics() {
  const [data, setData] = useState<BusinessAnalyticsData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [coverage, performance, financial, topQueries, report] = await Promise.all([
        businessAnalyticsApi.getCoverageAnalytics(),
        businessAnalyticsApi.getPerformanceAnalytics(),
        businessAnalyticsApi.getFinancialAnalytics(),
        businessAnalyticsApi.getTopQueriesAnalytics(20),
        businessAnalyticsApi.getCoverageReport(),
      ])
      setData({ coverage, performance, financial, topQueries, report })
    } catch {
      setError(es.common.errorAnalytics)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  return { data, isLoading, error, refresh }
}
