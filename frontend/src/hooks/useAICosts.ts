import { useCallback, useEffect, useState } from 'react'
import { getAICostSummary } from '../services/aiCostsApi'
import type { AICostSummary } from '../types/aiCosts'

export function useAICosts() {
  const [data, setData] = useState<AICostSummary | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const summary = await getAICostSummary()
      setData(summary)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  return { data, isLoading, error, refresh }
}
