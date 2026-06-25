import type {
  EnterpriseKnowledgeObject,
  KnowledgeListResponse,
  KnowledgeSchema,
  KnowledgeStatistics,
} from '../types/enterpriseKnowledge'
import { ChatApiError } from '../types/chat'
import { es } from '../i18n/spanish'

function getApiBaseUrl(): string {
  const base = import.meta.env.VITE_API_BASE_URL ?? ''
  return base.replace(/\/$/, '')
}

async function fetchJson<T>(path: string): Promise<T> {
  const url = `${getApiBaseUrl()}${path}`
  let response: Response
  try {
    response = await fetch(url, { method: 'GET', headers: { Accept: 'application/json' } })
  } catch {
    throw new ChatApiError(es.enterpriseKnowledge.errorLoad)
  }
  if (!response.ok) {
    throw new ChatApiError(es.enterpriseKnowledge.errorLoad)
  }
  return (await response.json()) as T
}

export async function listKnowledgeEntities(params: {
  search?: string
  page?: number
  page_size?: number
} = {}): Promise<KnowledgeListResponse> {
  const query = new URLSearchParams()
  if (params.search) query.set('search', params.search)
  if (params.page) query.set('page', String(params.page))
  if (params.page_size) query.set('page_size', String(params.page_size))
  const suffix = query.toString() ? `?${query.toString()}` : ''
  return fetchJson<KnowledgeListResponse>(`/api/knowledge/entities${suffix}`)
}

export async function getKnowledgeEntity(canonicalId: number): Promise<EnterpriseKnowledgeObject> {
  return fetchJson<EnterpriseKnowledgeObject>(`/api/knowledge/entities/${canonicalId}`)
}

export async function getKnowledgeStatistics(): Promise<KnowledgeStatistics> {
  return fetchJson<KnowledgeStatistics>('/api/knowledge/statistics')
}

export async function getKnowledgeSchema(): Promise<KnowledgeSchema> {
  return fetchJson<KnowledgeSchema>('/api/knowledge/schema')
}
