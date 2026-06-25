import { useCallback, useEffect, useState } from 'react'
import * as businessEntityApi from '../services/businessEntityApi'
import type {
  BusinessEntityListResponse,
  BusinessEntityStatistics,
  EntityListParams,
} from '../types/businessEntities'

export function useBusinessEntities(initialParams: EntityListParams = {}) {
  const [params, setParams] = useState<EntityListParams>({
    page: 1,
    page_size: 50,
    sort_by: 'movement_count',
    sort_dir: 'desc',
    ...initialParams,
  })
  const [list, setList] = useState<BusinessEntityListResponse | null>(null)
  const [statistics, setStatistics] = useState<BusinessEntityStatistics | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [listResponse, statsResponse] = await Promise.all([
        businessEntityApi.listBusinessEntities(params),
        businessEntityApi.getBusinessEntityStatistics(),
      ])
      setList(listResponse)
      setStatistics(statsResponse)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setIsLoading(false)
    }
  }, [params])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const updateParams = useCallback((patch: Partial<EntityListParams>) => {
    setParams((current) => ({
      ...current,
      ...patch,
      page: patch.page ?? (patch.search !== undefined || patch.source_column !== undefined ? 1 : current.page),
    }))
  }, [])

  return {
    list,
    statistics,
    params,
    isLoading,
    error,
    refresh,
    updateParams,
  }
}
