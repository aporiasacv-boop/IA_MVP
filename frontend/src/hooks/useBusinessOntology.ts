import { useCallback, useEffect, useState } from 'react'
import * as businessOntologyApi from '../services/businessOntologyApi'
import type { OntologyEntityView, OntologyListResponse, OntologyStatistics } from '../types/businessOntology'

export function useBusinessOntology() {
  const [ontology, setOntology] = useState<OntologyListResponse | null>(null)
  const [statistics, setStatistics] = useState<OntologyStatistics | null>(null)
  const [selected, setSelected] = useState<OntologyEntityView | null>(null)
  const [search, setSearch] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [ontologyResponse, statsResponse] = await Promise.all([
        businessOntologyApi.listBusinessOntology({ search: search || undefined, page_size: 30 }),
        businessOntologyApi.getOntologyStatistics(),
      ])
      setOntology(ontologyResponse)
      setStatistics(statsResponse)
      setSelected(ontologyResponse.items[0] ?? null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setIsLoading(false)
    }
  }, [search])

  useEffect(() => {
    void refresh()
  }, [refresh])

  return { ontology, statistics, selected, setSelected, search, setSearch, isLoading, error, refresh }
}
