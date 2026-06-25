import type {
  AdoptionMetrics,
  AuditOverview,
  CoverageGapItem,
  TopFailureItem,
  TopRouteItem,
} from '../types/operationalAudit'
import { ChatApiError } from '../types/chat'

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
    throw new ChatApiError('No fue posible obtener datos de auditoría operacional.')
  }
  if (!response.ok) {
    throw new ChatApiError('No fue posible obtener datos de auditoría operacional.')
  }
  return (await response.json()) as T
}

export async function getAuditOverview(): Promise<AuditOverview> {
  return fetchJson<AuditOverview>('/api/audit/overview')
}

export async function getCoverageGaps(limit = 50): Promise<CoverageGapItem[]> {
  return fetchJson<CoverageGapItem[]>(`/api/audit/coverage-gaps?limit=${limit}`)
}

export async function getTopRoutes(limit = 20): Promise<TopRouteItem[]> {
  return fetchJson<TopRouteItem[]>(`/api/audit/top-routes?limit=${limit}`)
}

export async function getTopFailures(limit = 50): Promise<TopFailureItem[]> {
  return fetchJson<TopFailureItem[]>(`/api/audit/top-failures?limit=${limit}`)
}

export async function getAdoptionMetrics(): Promise<AdoptionMetrics> {
  return fetchJson<AdoptionMetrics>('/api/audit/adoption')
}

export async function exportCoverageGaps(format: 'json' | 'csv'): Promise<Blob> {
  const url = `${getApiBaseUrl()}/api/audit/coverage-gaps/export?format=${format}`
  let response: Response
  try {
    response = await fetch(url, { method: 'GET' })
  } catch {
    throw new ChatApiError('No fue posible exportar coverage gaps.')
  }
  if (!response.ok) {
    throw new ChatApiError('No fue posible exportar coverage gaps.')
  }
  return response.blob()
}
