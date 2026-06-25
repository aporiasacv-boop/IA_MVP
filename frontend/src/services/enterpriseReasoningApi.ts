import type {
  EnterpriseReasoningObject,
  ReasoningListResponse,
  ReasoningRulesResponse,
  ReasoningStatistics,
} from '../types/enterpriseReasoning'
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
    throw new ChatApiError(es.enterpriseReasoning.errorLoad)
  }
  if (!response.ok) {
    throw new ChatApiError(es.enterpriseReasoning.errorLoad)
  }
  return (await response.json()) as T
}

export async function listReasoningEntities(params: {
  search?: string
  page?: number
  page_size?: number
} = {}): Promise<ReasoningListResponse> {
  const query = new URLSearchParams()
  if (params.search) query.set('search', params.search)
  if (params.page) query.set('page', String(params.page))
  if (params.page_size) query.set('page_size', String(params.page_size))
  const suffix = query.toString() ? `?${query.toString()}` : ''
  return fetchJson<ReasoningListResponse>(`/api/reasoning/entities${suffix}`)
}

export async function getReasoningEntity(canonicalId: number): Promise<EnterpriseReasoningObject> {
  return fetchJson<EnterpriseReasoningObject>(`/api/reasoning/entities/${canonicalId}`)
}

export async function getReasoningStatistics(): Promise<ReasoningStatistics> {
  return fetchJson<ReasoningStatistics>('/api/reasoning/statistics')
}

export async function getReasoningRules(): Promise<ReasoningRulesResponse> {
  return fetchJson<ReasoningRulesResponse>('/api/reasoning/rules')
}
