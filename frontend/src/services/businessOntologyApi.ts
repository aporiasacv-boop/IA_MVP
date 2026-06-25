import type {
  OntologyListResponse,
  OntologyStatistics,
  OntologyTypeItem,
} from '../types/businessOntology'
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
    throw new ChatApiError(es.businessOntology.errorLoad)
  }
  if (!response.ok) {
    throw new ChatApiError(es.businessOntology.errorLoad)
  }
  return (await response.json()) as T
}

export async function listBusinessOntology(params: {
  search?: string
  page?: number
  page_size?: number
} = {}): Promise<OntologyListResponse> {
  const query = new URLSearchParams()
  if (params.search) query.set('search', params.search)
  if (params.page) query.set('page', String(params.page))
  if (params.page_size) query.set('page_size', String(params.page_size))
  const suffix = query.toString() ? `?${query.toString()}` : ''
  return fetchJson<OntologyListResponse>(`/api/business-ontology${suffix}`)
}

export async function listOntologyTypes(conceptCategory?: string): Promise<{ items: OntologyTypeItem[]; total: number }> {
  const query = conceptCategory ? `?concept_category=${encodeURIComponent(conceptCategory)}` : ''
  return fetchJson(`/api/business-ontology/types${query}`)
}

export async function getOntologyStatistics(): Promise<OntologyStatistics> {
  return fetchJson<OntologyStatistics>('/api/business-ontology/statistics')
}
