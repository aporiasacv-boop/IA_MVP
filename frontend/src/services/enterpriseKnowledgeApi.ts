const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

export interface EnterpriseKnowledgeDocument {
  id: string
  title: string
  category: string
  path: string
  content: string
  provider?: string
  sections: Record<string, string>
}

export interface EnterpriseKnowledgeCategory {
  category: string
  label: string
  count: number
}

export interface EnterpriseKnowledgeProvider {
  id: string
  name: string
  status: string
  document_count: number
}

export interface EnterpriseKnowledgeStatistics {
  total_documents: number
  documents_by_category: Record<string, number>
  faq_entries: number
  knowledge_requests: number
  knowledge_runtime_hits: number
  knowledge_runtime_misses: number
  knowledge_runtime_cache_hits: number
  knowledge_runtime_reload_time_ms: number
  knowledge_runtime_last_refresh: string | null
  provider_distribution: Record<string, number>
  cache_hit_rate: number
  cache_size: number
  average_search_time_ms: number
  knowledge_sources: string[]
}

export interface EnterpriseKnowledgeHealth {
  status: string
  cache_valid: boolean
  total_documents: number
  cache_size: number
  cache_hit_rate: number
  last_refresh: string | null
  reload_time_ms: number
  active_providers: string[]
}

export interface EnterpriseKnowledgeProvidersResponse {
  active: EnterpriseKnowledgeProvider[]
  planned: EnterpriseKnowledgeProvider[]
}

export interface EnterpriseKnowledgeSearchResponse {
  query: string
  total: number
  items: EnterpriseKnowledgeDocument[]
  average_search_time_ms: number
}

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`)
  if (!response.ok) {
    throw new Error(`Error al consultar ${path}`)
  }
  return response.json() as Promise<T>
}

export function getEnterpriseKnowledgeHealth(): Promise<EnterpriseKnowledgeHealth> {
  return fetchJson('/api/enterprise-knowledge/health')
}

export function getEnterpriseKnowledgeStatistics(): Promise<EnterpriseKnowledgeStatistics> {
  return fetchJson('/api/enterprise-knowledge/statistics')
}

export function getEnterpriseKnowledgeProviders(): Promise<EnterpriseKnowledgeProvidersResponse> {
  return fetchJson('/api/enterprise-knowledge/providers')
}

export function searchEnterpriseKnowledge(query: string): Promise<EnterpriseKnowledgeSearchResponse> {
  const params = new URLSearchParams({ q: query })
  return fetchJson(`/api/enterprise-knowledge/search?${params.toString()}`)
}

export function getEnterpriseKnowledgeCategories(): Promise<{
  categories: EnterpriseKnowledgeCategory[]
  total_documents: number
}> {
  return fetchJson('/api/business-knowledge/categories')
}
