import { useCallback, useEffect, useState } from 'react'
import {
  getFinOpsForecast,
  getFinOpsOverview,
  getFinOpsProviders,
  getFinOpsSavings,
  type FinOpsForecast,
  type FinOpsOverview,
  type FinOpsProvider,
  type FinOpsSavings,
} from '../services/finopsApi'

export function useFinOps() {
  const [overview, setOverview] = useState<FinOpsOverview | null>(null)
  const [providers, setProviders] = useState<FinOpsProvider[]>([])
  const [savings, setSavings] = useState<FinOpsSavings | null>(null)
  const [forecast, setForecast] = useState<FinOpsForecast | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [overviewData, providersData, savingsData, forecastData] = await Promise.all([
        getFinOpsOverview(),
        getFinOpsProviders(),
        getFinOpsSavings(),
        getFinOpsForecast(),
      ])
      setOverview(overviewData)
      setProviders(providersData.providers)
      setSavings(savingsData)
      setForecast(forecastData)
    } catch {
      setError('No fue posible cargar las métricas FinOps.')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  return { overview, providers, savings, forecast, isLoading, error, refresh }
}
