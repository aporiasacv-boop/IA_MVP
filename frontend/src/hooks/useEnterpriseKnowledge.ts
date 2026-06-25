import { useCallback, useEffect, useState } from 'react'
import {
  getEnterpriseKnowledgeCategories,
  getEnterpriseKnowledgeHealth,
  getEnterpriseKnowledgeProviders,
  getEnterpriseKnowledgeStatistics,
  searchEnterpriseKnowledge,
  type EnterpriseKnowledgeDocument,
  type EnterpriseKnowledgeHealth,
  type EnterpriseKnowledgeProvidersResponse,
  type EnterpriseKnowledgeStatistics,
} from '../services/enterpriseKnowledgeApi'

export function useEnterpriseKnowledge() {
  const [statistics, setStatistics] = useState<EnterpriseKnowledgeStatistics | null>(null)
  const [health, setHealth] = useState<EnterpriseKnowledgeHealth | null>(null)
  const [providers, setProviders] = useState<EnterpriseKnowledgeProvidersResponse | null>(null)
  const [categories, setCategories] = useState<Awaited<
    ReturnType<typeof getEnterpriseKnowledgeCategories>
  > | null>(null)
  const [search, setSearch] = useState('')
  const [results, setResults] = useState<EnterpriseKnowledgeDocument[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [stats, healthData, providerData, categoryData] = await Promise.all([
        getEnterpriseKnowledgeStatistics(),
        getEnterpriseKnowledgeHealth(),
        getEnterpriseKnowledgeProviders(),
        getEnterpriseKnowledgeCategories(),
      ])
      setStatistics(stats)
      setHealth(healthData)
      setProviders(providerData)
      setCategories(categoryData)
    } catch {
      setError('No fue posible cargar el Servicio de Conocimiento.')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  useEffect(() => {
    if (!search.trim()) {
      setResults([])
      return
    }
    const timer = window.setTimeout(() => {
      void searchEnterpriseKnowledge(search.trim())
        .then((response) => setResults(response.items))
        .catch(() => setResults([]))
    }, 300)
    return () => window.clearTimeout(timer)
  }, [search])

  return {
    statistics,
    health,
    providers,
    categories,
    search,
    setSearch,
    results,
    isLoading,
    error,
    refresh,
  }
}
