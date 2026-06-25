import { useCallback, useEffect, useState } from 'react'
import * as enterpriseReasoningApi from '../services/enterpriseReasoningApi'
import type {
  EnterpriseReasoningObject,
  ReasoningListResponse,
  ReasoningStatistics,
} from '../types/enterpriseReasoning'

export function useEnterpriseReasoning() {
  const [list, setList] = useState<ReasoningListResponse | null>(null)
  const [statistics, setStatistics] = useState<ReasoningStatistics | null>(null)
  const [selected, setSelected] = useState<EnterpriseReasoningObject | null>(null)
  const [search, setSearch] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadDetail = useCallback(async (canonicalId: number) => {
    const detail = await enterpriseReasoningApi.getReasoningEntity(canonicalId)
    setSelected(detail)
  }, [])

  const refresh = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [listResponse, statsResponse] = await Promise.all([
        enterpriseReasoningApi.listReasoningEntities({ search: search || undefined, page_size: 30 }),
        enterpriseReasoningApi.getReasoningStatistics(),
      ])
      setList(listResponse)
      setStatistics(statsResponse)
      if (listResponse.items.length > 0) {
        await loadDetail(listResponse.items[0].canonical_id)
      } else {
        setSelected(null)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setIsLoading(false)
    }
  }, [search, loadDetail])

  const selectEntity = useCallback(
    async (canonicalId: number) => {
      setIsLoading(true)
      setError(null)
      try {
        await loadDetail(canonicalId)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error desconocido')
      } finally {
        setIsLoading(false)
      }
    },
    [loadDetail],
  )

  useEffect(() => {
    void refresh()
  }, [refresh])

  return {
    list,
    statistics,
    selected,
    selectEntity,
    search,
    setSearch,
    isLoading,
    error,
    refresh,
  }
}
