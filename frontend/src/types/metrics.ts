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

export interface HandledByDistributionItem {
  handled_by: string
  count: number
  success_rate: number
}

export interface RoutingPathItem {
  handled_by: string
  query_type: string
  count: number
}

export interface RoutingMetrics {
  handled_by_distribution: HandledByDistributionItem[]
  success_rate_by_handled_by: Record<string, number>
  top_paths: RoutingPathItem[]
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
