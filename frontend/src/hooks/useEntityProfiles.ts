import { useCallback, useEffect, useState } from 'react'
import * as entityProfileApi from '../services/entityProfileApi'
import type {
  EntityProfileItem,
  EntityProfileListResponse,
  EntityProfileStatistics,
} from '../types/entityProfiles'

export function useEntityProfiles() {
  const [profiles, setProfiles] = useState<EntityProfileListResponse | null>(null)
  const [statistics, setStatistics] = useState<EntityProfileStatistics | null>(null)
  const [selected, setSelected] = useState<EntityProfileItem | null>(null)
  const [search, setSearch] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [profileResponse, statsResponse] = await Promise.all([
        entityProfileApi.listEntityProfiles({ search: search || undefined, page_size: 30 }),
        entityProfileApi.getEntityProfileStatistics(),
      ])
      setProfiles(profileResponse)
      setStatistics(statsResponse)
      if (profileResponse.items.length > 0) {
        const detail = await entityProfileApi.getEntityProfile(profileResponse.items[0].canonical_id)
        setSelected(detail)
      } else {
        setSelected(null)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setIsLoading(false)
    }
  }, [search])

  const selectProfile = useCallback(async (canonicalId: number) => {
    try {
      const detail = await entityProfileApi.getEntityProfile(canonicalId)
      setSelected(detail)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  return {
    profiles,
    statistics,
    selected,
    search,
    setSearch,
    isLoading,
    error,
    refresh,
    selectProfile,
  }
}
