import type {
  BusinessExecutionPlan,
  SemanticParseResult,
  SemanticStatistics,
  VerbCatalogResponse,
} from '../types/semanticIntent'
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
    throw new ChatApiError(es.semanticIntent.errorLoad)
  }
  if (!response.ok) {
    throw new ChatApiError(es.semanticIntent.errorLoad)
  }
  return (await response.json()) as T
}

export async function getSemanticVerbs(): Promise<VerbCatalogResponse> {
  return fetchJson<VerbCatalogResponse>('/api/semantic-intent/verbs')
}

export async function getSemanticStatistics(): Promise<SemanticStatistics> {
  return fetchJson<SemanticStatistics>('/api/semantic-intent/statistics')
}

export async function parseSemanticQuestion(question: string): Promise<SemanticParseResult> {
  return fetchJson<SemanticParseResult>('/api/semantic-intent/parse', {
    method: 'POST',
    body: JSON.stringify({ question }),
  })
}

export async function planSemanticExecution(question: string): Promise<BusinessExecutionPlan> {
  return fetchJson<BusinessExecutionPlan>('/api/semantic-intent/plan', {
    method: 'POST',
    body: JSON.stringify({ question }),
  })
}
