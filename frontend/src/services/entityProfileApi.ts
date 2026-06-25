import type {
  EntityProfileItem,
  EntityProfileListResponse,
  EntityProfileStatistics,
} from '../types/entityProfiles'
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
    throw new ChatApiError(es.entityProfiles.errorLoad)
  }
  if (!response.ok) {
    throw new ChatApiError(es.entityProfiles.errorLoad)
  }
  return (await response.json()) as T
}

export async function listEntityProfiles(params: {
  search?: string
  sort_by?: string
  sort_dir?: 'asc' | 'desc'
  page?: number
  page_size?: number
} = {}): Promise<EntityProfileListResponse> {
  const query = new URLSearchParams()
  if (params.search) query.set('search', params.search)
  if (params.sort_by) query.set('sort_by', params.sort_by)
  if (params.sort_dir) query.set('sort_dir', params.sort_dir)
  if (params.page) query.set('page', String(params.page))
  if (params.page_size) query.set('page_size', String(params.page_size))
  const suffix = query.toString() ? `?${query.toString()}` : ''
  return fetchJson<EntityProfileListResponse>(`/api/entity-profiles${suffix}`)
}

export async function getEntityProfile(canonicalId: number): Promise<EntityProfileItem> {
  return fetchJson<EntityProfileItem>(`/api/entity-profiles/${canonicalId}`)
}

export async function getEntityProfileStatistics(): Promise<EntityProfileStatistics> {
  return fetchJson<EntityProfileStatistics>('/api/entity-profiles/statistics')
}
