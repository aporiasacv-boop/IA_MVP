import type {
  CanonicalEntityListResponse,
  CanonicalStatistics,
  CanonicalSuggestionListResponse,
} from '../types/canonicalEntities'
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
    throw new ChatApiError(es.canonicalEntities.errorLoad)
  }
  if (!response.ok) {
    throw new ChatApiError(es.canonicalEntities.errorLoad)
  }
  return (await response.json()) as T
}

export async function listCanonicalEntities(params: {
  search?: string
  sort_by?: string
  sort_dir?: 'asc' | 'desc'
  page?: number
  page_size?: number
} = {}): Promise<CanonicalEntityListResponse> {
  const query = new URLSearchParams()
  if (params.search) query.set('search', params.search)
  if (params.sort_by) query.set('sort_by', params.sort_by)
  if (params.sort_dir) query.set('sort_dir', params.sort_dir)
  if (params.page) query.set('page', String(params.page))
  if (params.page_size) query.set('page_size', String(params.page_size))
  const suffix = query.toString() ? `?${query.toString()}` : ''
  return fetchJson<CanonicalEntityListResponse>(`/api/canonical-entities${suffix}`)
}

export async function listCanonicalSuggestions(params: {
  status?: string
  min_score?: number
  page?: number
  page_size?: number
} = {}): Promise<CanonicalSuggestionListResponse> {
  const query = new URLSearchParams()
  if (params.status) query.set('status', params.status)
  if (params.min_score !== undefined) query.set('min_score', String(params.min_score))
  if (params.page) query.set('page', String(params.page))
  if (params.page_size) query.set('page_size', String(params.page_size))
  const suffix = query.toString() ? `?${query.toString()}` : ''
  return fetchJson<CanonicalSuggestionListResponse>(`/api/canonical-entities/suggestions${suffix}`)
}

export async function getCanonicalStatistics(): Promise<CanonicalStatistics> {
  return fetchJson<CanonicalStatistics>('/api/canonical-entities/statistics')
}
