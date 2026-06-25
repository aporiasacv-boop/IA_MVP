export interface PerformanceMetrics {
  totalQueries: number
  deterministicQueries: number
  generativeQueries: number
  averageResponseMs: number
  tokensSaved: number
  estimatedCostAvoidedUsd: number
  llmCallsAvoided: number
}

export interface SavingsExample {
  question: string
  traditionalTokens: number
  actualTokens: number
  savingsPercent: number
  traditionalTimeMs: number
  actualTimeMs: number
}

export interface CostOptimizationExample {
  question: string
  llmTokensEstimate: number
  actualTokens: number
  savingsPercent: number
}

export interface PerformanceRecord {
  question: string
  response_mode: 'DETERMINISTIC' | 'GENERATIVE'
  total_ms: number
  llm_ms: number
  estimated_tokens: number
  intent: string
  recorded_at: string
}
