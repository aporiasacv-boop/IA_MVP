const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

export type DecisionType =
  | 'proveedor_ia'
  | 'escenario'
  | 'infraestructura'
  | 'estrategia_despliegue'
  | 'optimizacion_costos'
  | 'optimizacion_ia'
  | 'optimizacion_pipeline'

export interface DecisionRecommendRequest {
  decision_type: DecisionType
  scenario_id?: string
  question?: string | null
}

export interface EvidenceItem {
  evidence_id: string
  source: string
  category: string
  metric: string
  value: string
  confidence: number
  rule?: string | null
}

export interface FinancialImpact {
  cost_usd: number
  cost_mxn: number
  avoided_cost_usd: number
  roi_pct: number
  llm_avoidance_rate: number
  monthly_projection_usd: number
}

export interface RecommendationItem {
  title: string
  detail: string
  decision_type: string
  evidence_ids: string[]
  confidence: number
}

export interface EnterpriseDecisionPackage {
  package_id: string
  decision_type: string
  executive_summary: string
  findings: string[]
  evidence_used: EvidenceItem[]
  scenarios_considered: Array<{
    scenario_id: string
    scenario_name: string
    cost_usd: number
    avoided_cost_usd: number
    llm_avoidance_rate: number
  }>
  financial_impact: FinancialImpact
  risks: string[]
  opportunities: string[]
  main_recommendation: RecommendationItem
  alternative_recommendations: RecommendationItem[]
  confidence_level: number
  limitations: string[]
  sources_used: string[]
}

export interface DecisionSchemaResponse {
  schema_id: string
  schema_version: string
  decision_types: string[]
  required_sections: string[]
  description: string
}

export interface DecisionStatisticsResponse {
  decision_requests: number
  recommendation_types: Record<string, number>
  average_confidence: number
  average_financial_impact: number
  decision_sources: string[]
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    ...init,
  })
  if (!response.ok) {
    throw new Error(`Error ${response.status}`)
  }
  return response.json() as Promise<T>
}

export function getDecisionSchema(): Promise<DecisionSchemaResponse> {
  return request('/api/decision/schema')
}

export function getDecisionStatistics(): Promise<DecisionStatisticsResponse> {
  return request('/api/decision/statistics')
}

export function getDecisionExample(): Promise<EnterpriseDecisionPackage> {
  return request('/api/decision/example')
}

export function postDecisionRecommend(body: DecisionRecommendRequest): Promise<EnterpriseDecisionPackage> {
  return request('/api/decision/recommend', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}
