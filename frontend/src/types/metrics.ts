export interface MetricsSummary {
  total_requests: number
  business_pipeline_requests: number
  legacy_chat_requests: number
  guided_fallback_requests: number
  capability_discovery_requests: number
  suggested_questions_generated: number
  average_suggestions_per_response: number
  slot_clarification_requests: number
  conversation_memory_requests: number
  avg_total_time_ms: number
  avg_database_time_ms: number | null
  avg_ollama_time_ms: number | null
}

export interface TopQueryItem {
  question: string
  count: number
}

export interface PerformanceStats {
  p50_total_time_ms: number
  p95_total_time_ms: number
  p99_total_time_ms: number
  averages: Record<string, number | null>
}
