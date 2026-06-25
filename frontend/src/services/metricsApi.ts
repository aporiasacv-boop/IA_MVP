import type { MetricsSummary, PerformanceStats, TopQueryItem } from '../types/metrics'
import { ChatApiError } from '../types/chat'

function getApiBaseUrl(): string {
  const base = import.meta.env.VITE_API_BASE_URL ?? ''
  return base.replace(/\/$/, '')
}

async function fetchJson<T>(path: string): Promise<T> {
  const baseUrl = getApiBaseUrl()
  const url = `${baseUrl}${path}`

  let response: Response
  try {
    response = await fetch(url, {
      method: 'GET',
      headers: { Accept: 'application/json' },
    })
  } catch {
    throw new ChatApiError('No fue posible obtener métricas del sistema.')
  }

  if (!response.ok) {
    throw new ChatApiError('No fue posible obtener métricas del sistema.')
  }

  try {
    return (await response.json()) as T
  } catch {
    throw new ChatApiError('No fue posible obtener métricas del sistema.')
  }
}

export async function getSummary(): Promise<MetricsSummary> {
  return fetchJson<MetricsSummary>('/api/metrics/summary')
}

export async function getPerformance(): Promise<PerformanceStats> {
  return fetchJson<PerformanceStats>('/api/metrics/performance')
}

export async function getTopQueries(limit = 10): Promise<TopQueryItem[]> {
  const query = new URLSearchParams({ limit: String(limit) })
  return fetchJson<TopQueryItem[]>(`/api/metrics/top-queries?${query}`)
}
