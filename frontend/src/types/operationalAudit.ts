export interface AuditOverview {
  total_requests: number
  total_successes: number
  total_failures: number
  business_pipeline_pct: number
  memory_pct: number
  clarification_pct: number
  capability_pct: number
  fallback_pct: number
  legacy_pct: number
  coverage_score: number
  coverage_gap_score: number
}

export interface CoverageGapItem {
  question: string
  count: number
  route: string
}

export interface TopRouteItem {
  route: string
  count: number
  percentage: number
}

export interface TopFailureItem {
  question: string
  route: string
  frequency: number
}

export interface AdoptionMetrics {
  suggested_questions_usage: number
  conversation_memory_usage: number
  slot_clarification_usage: number
  capability_discovery_usage: number
}

export interface OperationalAuditData {
  overview: AuditOverview
  coverageGaps: CoverageGapItem[]
  topFailures: TopFailureItem[]
  topRoutes: TopRouteItem[]
  adoption: AdoptionMetrics
}
