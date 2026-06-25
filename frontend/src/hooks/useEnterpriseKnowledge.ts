import { useCallback, useEffect, useState } from 'react'
import * as enterpriseKnowledgeApi from '../services/enterpriseKnowledgeApi'
import type {
  EnterpriseKnowledgeObject,
  KnowledgeListResponse,
  KnowledgeStatistics,
} from '../types/enterpriseKnowledge'

export function useEnterpriseKnowledge() {
  const [list, setList] = useState<KnowledgeListResponse | null>(null)
  const [statistics, setStatistics] = useState<KnowledgeStatistics | null>(null)
  const [selected, setSelected] = useState<EnterpriseKnowledgeObject | null>(null)
  const [search, setSearch] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadDetail = useCallback(async (canonicalId: number) => {
    const detail = await enterpriseKnowledgeApi.getKnowledgeEntity(canonicalId)
    setSelected(detail)
  }, [])

  const refresh = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [listResponse, statsResponse] = await Promise.all([
        enterpriseKnowledgeApi.listKnowledgeEntities({ search: search || undefined, page_size: 30 }),
        enterpriseKnowledgeApi.getKnowledgeStatistics(),
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
