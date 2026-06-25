import type {
  EnterpriseEvidencePackage,
  EvidenceSchema,
  EvidenceStatistics,
} from '../types/evidencePackage'
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
    throw new ChatApiError(es.evidencePackage.errorLoad)
  }
  if (!response.ok) {
    throw new ChatApiError(es.evidencePackage.errorLoad)
  }
  return (await response.json()) as T
}

export async function buildEvidencePackage(question: string, canonicalId?: number): Promise<EnterpriseEvidencePackage> {
  return fetchJson<EnterpriseEvidencePackage>('/api/evidence/build', {
    method: 'POST',
    body: JSON.stringify({ question, canonical_id: canonicalId ?? null }),
  })
}

export async function getEvidenceExample(): Promise<EnterpriseEvidencePackage> {
  return fetchJson<EnterpriseEvidencePackage>('/api/evidence/example')
}

export async function getEvidenceStatistics(): Promise<EvidenceStatistics> {
  return fetchJson<EvidenceStatistics>('/api/evidence/statistics')
}

export async function getEvidenceSchema(): Promise<EvidenceSchema> {
  return fetchJson<EvidenceSchema>('/api/evidence/schema')
}
