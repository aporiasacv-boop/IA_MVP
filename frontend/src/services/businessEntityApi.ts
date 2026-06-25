import type {
  BusinessEntityItem,
  BusinessEntityListResponse,
  BusinessEntityStatistics,
  EntityListParams,
} from '../types/businessEntities'
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
    response = await fetch(url, {
      method: 'GET',
      headers: { Accept: 'application/json' },
    })
  } catch {
    throw new ChatApiError(es.businessEntities.errorLoad)
  }
  if (!response.ok) {
    throw new ChatApiError(es.businessEntities.errorLoad)
  }
  return (await response.json()) as T
}

function buildQuery(params: EntityListParams): string {
  const query = new URLSearchParams()
  if (params.search) query.set('search', params.search)
  if (params.source_column) query.set('source_column', params.source_column)
  if (params.classification_status) {
    query.set('classification_status', params.classification_status)
  }
  if (params.sort_by) query.set('sort_by', params.sort_by)
  if (params.sort_dir) query.set('sort_dir', params.sort_dir)
  if (params.page) query.set('page', String(params.page))
  if (params.page_size) query.set('page_size', String(params.page_size))
  const serialized = query.toString()
  return serialized ? `?${serialized}` : ''
}

export async function listBusinessEntities(
  params: EntityListParams = {},
): Promise<BusinessEntityListResponse> {
  return fetchJson<BusinessEntityListResponse>(
    `/api/business-entities${buildQuery(params)}`,
  )
}

export async function getBusinessEntityByCode(
  entityCode: string,
  sourceColumn?: string,
): Promise<BusinessEntityItem[]> {
  const suffix = sourceColumn
    ? `?source_column=${encodeURIComponent(sourceColumn)}`
    : ''
  return fetchJson<BusinessEntityItem[]>(
    `/api/business-entities/${encodeURIComponent(entityCode)}${suffix}`,
  )
}

export async function getBusinessEntityStatistics(): Promise<BusinessEntityStatistics> {
  return fetchJson<BusinessEntityStatistics>('/api/business-entities/statistics')
}
