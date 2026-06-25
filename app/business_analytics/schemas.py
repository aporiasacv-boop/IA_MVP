from datetime import datetime

from pydantic import BaseModel, Field


class CoverageAnalyticsResponse(BaseModel):
    total_requests: int
    business_pipeline: int
    slot_clarification: int
    conversation_memory: int
    capability_discovery: int
    guided_fallback: int
    legacy_chat: int
    business_pipeline_pct: float
    slot_clarification_pct: float
    conversation_memory_pct: float
    capability_discovery_pct: float
    guided_fallback_pct: float
    legacy_chat_pct: float


class PerformanceAnalyticsResponse(BaseModel):
    p50_ms: float
    p95_ms: float
    p99_ms: float
    avg_intent_ms: float
    avg_planner_ms: float
    avg_executor_ms: float
    avg_response_ms: float
    avg_total_ms: float


class FinancialAnalyticsResponse(BaseModel):
    total_requests: int
    deterministic_requests: int
    ai_requests: int
    ai_avoidance_rate: float
    legacy_dependency_rate: float
    estimated_monthly_requests: int
    estimated_gpt_equivalent_calls: int
    estimated_claude_equivalent_calls: int
    estimated_ollama_calls: int
    estimated_gpt_cost: float
    estimated_claude_cost: float
    estimated_ollama_cost: float


class TopQueryAnalyticsItem(BaseModel):
    question: str
    count: int
    route: str
    success_rate: float


class TopRouteItem(BaseModel):
    handled_by: str
    query_type: str
    count: int
    success_rate: float = 0.0


class CoverageReportResponse(BaseModel):
    coverage_score: float
    success_rate: float
    deterministic_rate: float
    legacy_rate: float
    top_routes: list[TopRouteItem] = Field(default_factory=list)
    business_entities_total: int = 0
    business_entities_loaded: int = 0
    duplicated_entities: int = 0
    last_entity_refresh: datetime | None = None
    canonical_entities_total: int = 0
    canonical_matches: int = 0
    pending_matches: int = 0
    automatic_suggestions: int = 0
    entity_profiles_total: int = 0
    average_profile_completeness: float = 0.0
    profile_generation_time: float = 0.0
    last_profile_refresh: datetime | None = None
    ontology_entities: int = 0
    ontology_pending: int = 0
    ontology_approved: int = 0
    ontology_rules: int = 0
    ontology_average_confidence: float = 0.0
    knowledge_objects_total: int = 0
    knowledge_build_time: float = 0.0
    knowledge_average_completeness: float = 0.0
    knowledge_average_confidence: float = 0.0
    knowledge_last_refresh: datetime | None = None
    reasoning_objects_total: int = 0
    reasoning_rules_executed: int = 0
    average_reasoning_confidence: float = 0.0
    average_findings: float = 0.0
    average_alerts: float = 0.0
    average_recommendations: float = 0.0
    last_reasoning_refresh: datetime | None = None
    semantic_parses: int = 0
    execution_plans: int = 0
    verb_distribution: dict[str, int] = Field(default_factory=dict)
    average_semantic_confidence: float = 0.0
    planner_success_rate: float = 0.0
    unknown_verbs: int = 0
    evidence_packages_total: int = 0
    average_package_size: float = 0.0
    average_evidence_items: float = 0.0
    average_evidence_confidence: float = 0.0
    missing_evidence: int = 0
    package_build_time: float = 0.0
    llm_requests: int = 0
    provider_distribution: dict[str, int] = Field(default_factory=dict)
    tokens_input: int = 0
    tokens_output: int = 0
    estimated_llm_cost: float = 0.0
    average_llm_latency: float = 0.0
    average_cost_per_question: float = 0.0
    hallucination_guard_triggered: int = 0
    llm_fallbacks: int = 0
    knowledge_runtime_hits: int = 0
    knowledge_runtime_misses: int = 0
    knowledge_runtime_cache_hits: int = 0
    knowledge_runtime_reload_time: float = 0.0
    knowledge_runtime_last_refresh: datetime | None = None
    knowledge_runtime_documents: int = 0
    knowledge_requests: int = 0
    knowledge_provider_distribution: dict[str, int] = Field(default_factory=dict)
    cache_hit_rate: float = 0.0
    cache_size: int = 0
    average_search_time: float = 0.0
    knowledge_sources: list[str] = Field(default_factory=list)
