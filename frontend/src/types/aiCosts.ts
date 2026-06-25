export interface ProviderCostItem {
  provider: string
  requests: number
  tokens_input: number
  tokens_output: number
  estimated_cost: number
  average_latency: number
}

export interface AICostSummary {
  llm_requests: number
  provider_distribution: Record<string, number>
  tokens_input: number
  tokens_output: number
  estimated_cost: number
  average_latency: number
  average_cost_per_question: number
  hallucination_guard_triggered: number
  llm_fallbacks: number
  cost_by_provider: ProviderCostItem[]
  daily_cost: number
  monthly_cost: number
  cost_per_user: Record<string, number>
  cost_per_query: number
  provider_comparison: ProviderCostItem[]
}

export interface ExecutiveResponse {
  executive_summary: string
  detailed_analysis: string
  confidence: number
  citations: Array<{ key: string; source: string; confidence?: number }>
  limitations: string[]
  provider: string
  model: string
  tokens_input: number
  tokens_output: number
  estimated_cost: number
  response_time: number
  hallucination_guard_triggered: boolean
  evidence_package_id?: string | null
}
