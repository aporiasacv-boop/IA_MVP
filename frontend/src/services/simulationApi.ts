const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

export interface SimulationScenarioInput {
  scenario_id: string
  name: string
  users: number
  queries_per_user_day: number
  business_pipeline_pct?: number | null
  knowledge_service_pct?: number | null
  conversation_memory_pct?: number | null
  executive_reasoning_pct?: number | null
  legacy_chat_pct?: number | null
  llm_provider: string
  llm_model?: string
  cost_per_1k_input_tokens?: number | null
  cost_per_1k_output_tokens?: number | null
  concurrency: number
  peak_hours: number
  working_days: number
}

export interface SimulationMetrics {
  queries_per_day: number
  queries_per_month: number
  total_tokens: number
  cost_usd: number
  cost_mxn: number
  avoided_cost_usd: number
  llm_avoidance_rate: number
  knowledge_savings_usd: number
  pipeline_savings_usd: number
  memory_savings_usd: number
  avg_latency_ms: number
  latency_p50_ms: number
  latency_p95_ms: number
  latency_p99_ms: number
  estimated_cpu_cores: number
  estimated_ram_gb: number
  estimated_gpu_gb: number
  roi_pct: number
}

export interface ProviderSimulation {
  provider: string
  cost_usd: number
  cost_mxn: number
  avg_latency_ms: number
  avoided_cost_usd: number
  roi_pct: number
  participation_pct: number
}

export interface SimulationRunResponse {
  scenario_id: string
  scenario_name: string
  baseline_source: string
  metrics: SimulationMetrics
  provider_comparison: ProviderSimulation[]
}

export interface PredefinedScenario {
  id: string
  name: string
  description: string
  defaults: SimulationScenarioInput
}

export interface SimulationScenariosResponse {
  baseline: { source: string; total_historical_queries: number }
  predefined: PredefinedScenario[]
}

export interface SimulationRecommendation {
  category: string
  title: string
  detail: string
  metric_value: string
}

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init)
  if (!response.ok) {
    throw new Error(`Error al consultar ${path}`)
  }
  return response.json() as Promise<T>
}

export function getSimulationScenarios(): Promise<SimulationScenariosResponse> {
  return fetchJson('/api/simulation/scenarios')
}

export function runSimulation(scenario: SimulationScenarioInput): Promise<SimulationRunResponse> {
  return fetchJson('/api/simulation/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(scenario),
  })
}

export function getSimulationRecommendations(): Promise<{ recommendations: SimulationRecommendation[] }> {
  return fetchJson('/api/simulation/recommendations')
}
