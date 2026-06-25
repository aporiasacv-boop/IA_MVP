export interface CoverageAnalytics {
  total_requests: number
  business_pipeline: number
  slot_clarification: number
  conversation_memory: number
  capability_discovery: number
  guided_fallback: number
  legacy_chat: number
  business_pipeline_pct: number
  slot_clarification_pct: number
  conversation_memory_pct: number
  capability_discovery_pct: number
  guided_fallback_pct: number
  legacy_chat_pct: number
}

export interface PerformanceAnalytics {
  p50_ms: number
  p95_ms: number
  p99_ms: number
  avg_intent_ms: number
  avg_planner_ms: number
  avg_executor_ms: number
  avg_response_ms: number
  avg_total_ms: number
}

export interface FinancialAnalytics {
  total_requests: number
  deterministic_requests: number
  ai_requests: number
  ai_avoidance_rate: number
  legacy_dependency_rate: number
  estimated_monthly_requests: number
  estimated_gpt_equivalent_calls: number
  estimated_claude_equivalent_calls: number
  estimated_ollama_calls: number
  estimated_gpt_cost: number
  estimated_claude_cost: number
  estimated_ollama_cost: number
}

export interface TopQueryAnalyticsItem {
  question: string
  count: number
  route: string
  success_rate: number
}

export interface CoverageReport {
  coverage_score: number
  success_rate: number
  deterministic_rate: number
  legacy_rate: number
  top_routes: Array<{
    handled_by: string
    query_type: string
    count: number
    success_rate: number
  }>
  business_entities_total?: number
  business_entities_loaded?: number
  duplicated_entities?: number
  last_entity_refresh?: string | null
  canonical_entities_total?: number
  canonical_matches?: number
  pending_matches?: number
  automatic_suggestions?: number
  entity_profiles_total?: number
  average_profile_completeness?: number
  profile_generation_time?: number
  last_profile_refresh?: string | null
  ontology_entities?: number
  ontology_pending?: number
  ontology_approved?: number
  ontology_rules?: number
  ontology_average_confidence?: number
  knowledge_objects_total?: number
  knowledge_build_time?: number
  knowledge_average_completeness?: number
  knowledge_average_confidence?: number
  knowledge_last_refresh?: string | null
  reasoning_objects_total?: number
  reasoning_rules_executed?: number
  average_reasoning_confidence?: number
  average_findings?: number
  average_alerts?: number
  average_recommendations?: number
  last_reasoning_refresh?: string | null
  semantic_parses?: number
  execution_plans?: number
  verb_distribution?: Record<string, number>
  average_semantic_confidence?: number
  planner_success_rate?: number
  unknown_verbs?: number
  evidence_packages_total?: number
  average_package_size?: number
  average_evidence_items?: number
  average_evidence_confidence?: number
  missing_evidence?: number
  package_build_time?: number
}

export interface BusinessAnalyticsData {
  coverage: CoverageAnalytics
  performance: PerformanceAnalytics
  financial: FinancialAnalytics
  topQueries: TopQueryAnalyticsItem[]
  report: CoverageReport
}
