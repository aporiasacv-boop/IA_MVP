const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

export interface FinOpsOverview {
  total_queries: number
  total_cost_usd: number
  total_cost_mxn: number
  cost_today_usd: number
  cost_month_usd: number
  cost_year_projected_usd: number
  avg_cost_per_query_usd: number
  avg_cost_per_session_usd: number
  avg_cost_per_user_usd: number
  llm_queries: number
  deterministic_queries: number
  llm_avoidance_rate: number
  knowledge_avoidance_rate: number
  pipeline_avoidance_rate: number
  total_avoided_cost_usd: number
  accumulated_savings_usd: number
  real_token_queries: number
  estimated_token_queries: number
  real_cost_share: number
}

export interface FinOpsProvider {
  provider: string
  requests: number
  tokens_input: number
  tokens_output: number
  total_tokens: number
  cost_usd: number
  average_latency_ms: number
  participation_pct: number
}

export interface FinOpsSavings {
  llm_avoidance_rate: number
  knowledge_avoidance_rate: number
  pipeline_avoidance_rate: number
  total_avoided_cost_usd: number
  accumulated_savings_usd: number
  by_route: Array<{
    handled_by: string
    queries: number
    avoided_cost_usd: number
    share_pct: number
  }>
}

export interface FinOpsForecastScenario {
  users: number
  estimated_queries: number
  cost_openai_usd: number
  cost_claude_usd: number
  cost_ollama_usd: number
  estimated_cpu_cores: number
  estimated_ram_gb: number
  estimated_gpu_gb: number
  estimated_tokens: number
  estimated_latency_ms: number
}

export interface FinOpsForecast {
  scenarios: FinOpsForecastScenario[]
  assumptions: Record<string, string>
}

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`)
  if (!response.ok) {
    throw new Error(`Error al consultar ${path}`)
  }
  return response.json() as Promise<T>
}

export function getFinOpsOverview(): Promise<FinOpsOverview> {
  return fetchJson('/api/finops/overview')
}

export function getFinOpsProviders(): Promise<{ providers: FinOpsProvider[]; total_requests: number }> {
  return fetchJson('/api/finops/providers')
}

export function getFinOpsSavings(): Promise<FinOpsSavings> {
  return fetchJson('/api/finops/savings')
}

export function getFinOpsForecast(): Promise<FinOpsForecast> {
  return fetchJson('/api/finops/forecast')
}
