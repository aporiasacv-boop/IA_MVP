export interface ExecutiveAgendaItem {
  title: string
  summary: string
  justification: string
  priority: string
  expected_impact: string
  suggested_query: string
  action_label: string
}

export interface ExecutiveAgenda {
  greeting: string
  items: ExecutiveAgendaItem[]
}

export interface ExecutiveAgendaResponse {
  agenda: ExecutiveAgenda
  advisor_generation_ms: number
  advisor_provider?: string | null
  advisor_model?: string | null
  advisor_items: number
  advisor_fallback_used: boolean
}

export interface ExecutiveAgendaParams {
  sessionId?: string
  period?: string | null
  scenario?: string | null
}

function getApiBaseUrl(): string {
  const base = import.meta.env.VITE_API_BASE_URL ?? ''
  return base.replace(/\/$/, '')
}

export async function fetchExecutiveAgenda(
  params: ExecutiveAgendaParams = {},
): Promise<ExecutiveAgendaResponse> {
  const search = new URLSearchParams()
  if (params.sessionId) search.set('session_id', params.sessionId)
  if (params.period) search.set('period', params.period)
  if (params.scenario) search.set('scenario', params.scenario)

  const query = search.toString()
  const url = `${getApiBaseUrl()}/api/executive-advisor/agenda${query ? `?${query}` : ''}`

  const response = await fetch(url, {
    headers: { Accept: 'application/json' },
  })

  if (!response.ok) {
    throw new Error('No fue posible cargar la Agenda Ejecutiva.')
  }

  return response.json() as Promise<ExecutiveAgendaResponse>
}

export function agendaFromHybridMetadata(
  metadata: Record<string, unknown>,
): ExecutiveAgendaResponse | null {
  const rawAgenda = metadata.executive_advisor_agenda
  if (!rawAgenda || typeof rawAgenda !== 'object') return null

  const agenda = rawAgenda as ExecutiveAgenda
  if (!Array.isArray(agenda.items) || agenda.items.length === 0) return null

  return {
    agenda,
    advisor_generation_ms: readNumber(metadata.advisor_generation_ms),
    advisor_provider: readString(metadata.advisor_provider),
    advisor_model: readString(metadata.advisor_model),
    advisor_items: readNumber(metadata.advisor_items) || agenda.items.length,
    advisor_fallback_used: metadata.advisor_fallback_used === true,
  }
}

function readString(value: unknown): string | null {
  return typeof value === 'string' ? value : null
}

function readNumber(value: unknown): number {
  return typeof value === 'number' ? value : 0
}
