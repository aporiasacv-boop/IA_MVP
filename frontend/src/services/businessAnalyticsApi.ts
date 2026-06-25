import type {
  CoverageAnalytics,
  CoverageReport,
  FinancialAnalytics,
  PerformanceAnalytics,
  TopQueryAnalyticsItem,
} from '../types/businessAnalytics'
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
    throw new ChatApiError(es.common.errorAnalytics)
  }
  if (!response.ok) {
    throw new ChatApiError(es.common.errorAnalytics)
  }
  return (await response.json()) as T
}

export async function getCoverageAnalytics(): Promise<CoverageAnalytics> {
  return fetchJson<CoverageAnalytics>('/api/analytics/coverage')
}

export async function getPerformanceAnalytics(): Promise<PerformanceAnalytics> {
  return fetchJson<PerformanceAnalytics>('/api/analytics/performance')
}

export async function getFinancialAnalytics(): Promise<FinancialAnalytics> {
  return fetchJson<FinancialAnalytics>('/api/analytics/financial')
}

export async function getTopQueriesAnalytics(
  limit = 20,
): Promise<TopQueryAnalyticsItem[]> {
  return fetchJson<TopQueryAnalyticsItem[]>(`/api/analytics/top-queries?limit=${limit}`)
}

export async function getCoverageReport(): Promise<CoverageReport> {
  return fetchJson<CoverageReport>('/api/analytics/report')
}
