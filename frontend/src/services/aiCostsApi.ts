import type { AICostSummary, ExecutiveResponse } from '../types/aiCosts'
import { ChatApiError } from '../types/chat'
import { es } from '../i18n/spanish'

function getApiBaseUrl(): string {
  const base = import.meta.env.VITE_API_BASE_URL ?? ''
  return base.replace(/\/$/, '')
}

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${getApiBaseUrl()}${path}`
  let response: Response
  try {
    response = await fetch(url, {
      ...init,
      headers: { Accept: 'application/json', 'Content-Type': 'application/json', ...init?.headers },
    })
  } catch {
    throw new ChatApiError(es.aiCosts.errorLoad)
  }
  if (!response.ok) {
    throw new ChatApiError(es.aiCosts.errorLoad)
  }
  return (await response.json()) as T
}

export async function getAICostSummary(): Promise<AICostSummary> {
  return fetchJson<AICostSummary>('/api/ai-costs/summary')
}

export async function generateExecutiveResponse(question: string): Promise<ExecutiveResponse> {
  return fetchJson<ExecutiveResponse>('/api/executive-response/generate', {
    method: 'POST',
    body: JSON.stringify({ question }),
  })
}

export async function getExecutiveStatistics(): Promise<Record<string, unknown>> {
  return fetchJson<Record<string, unknown>>('/api/executive-response/statistics')
}
