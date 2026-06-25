import { useCallback, useEffect, useState } from 'react'
import * as canonicalEntityApi from '../services/canonicalEntityApi'
import type {
  CanonicalEntityListResponse,
  CanonicalStatistics,
  CanonicalSuggestionListResponse,
} from '../types/canonicalEntities'

export function useCanonicalEntities() {
  const [canonicals, setCanonicals] = useState<CanonicalEntityListResponse | null>(null)
  const [suggestions, setSuggestions] = useState<CanonicalSuggestionListResponse | null>(null)
  const [statistics, setStatistics] = useState<CanonicalStatistics | null>(null)
  const [search, setSearch] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [canonicalResponse, suggestionResponse, statsResponse] = await Promise.all([
        canonicalEntityApi.listCanonicalEntities({ search: search || undefined, page_size: 30 }),
        canonicalEntityApi.listCanonicalSuggestions({ status: 'pending', page_size: 30, min_score: 0.7 }),
        canonicalEntityApi.getCanonicalStatistics(),
      ])
      setCanonicals(canonicalResponse)
      setSuggestions(suggestionResponse)
      setStatistics(statsResponse)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setIsLoading(false)
    }
  }, [search])

  useEffect(() => {
    void refresh()
  }, [refresh])

  return { canonicals, suggestions, statistics, search, setSearch, isLoading, error, refresh }
}
