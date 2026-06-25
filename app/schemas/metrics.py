from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TopDomainItem(BaseModel):
    domain: str
    count: int


class MetricsSummaryResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "total_requests": 1000,
            "business_pipeline_requests": 720,
            "legacy_chat_requests": 280,
            "guided_fallback_requests": 45,
            "capability_discovery_requests": 35,
            "slot_clarification_requests": 30,
            "conversation_memory_requests": 25,
            "avg_total_time_ms": 85.3,
            "avg_database_time_ms": 22.1,
            "avg_ollama_time_ms": 1800.0,
        }
    })

    total_requests: int
    business_pipeline_requests: int
    legacy_chat_requests: int
    guided_fallback_requests: int = 0
    capability_discovery_requests: int = 0
    slot_clarification_requests: int = 0
    conversation_memory_requests: int = 0
    suggested_questions_generated: int = 0
    average_suggestions_per_response: float = 0.0
    avg_total_time_ms: float
    avg_database_time_ms: float | None = None
    avg_ollama_time_ms: float | None = None
    coverage_recovery_hits: int = 0
    coverage_recovery_misses: int = 0
    capability_discovery_v2_responses: int = 0
    capability_discovery_response_length: int = 0
    domain_detected: str | None = None
    domain_fallback_hits: int = 0
    domain_fallback_misses: int = 0
    top_domains: list[TopDomainItem] = Field(default_factory=list)
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
    executive_reasoning_requests: int = 0


class HandledByDistributionItem(BaseModel):
    handled_by: str
    count: int
    success_rate: float


class RoutingPathItem(BaseModel):
    handled_by: str
    query_type: str
    count: int


class RoutingMetricsResponse(BaseModel):
    handled_by_distribution: list[HandledByDistributionItem]
    success_rate_by_handled_by: dict[str, float]
    top_paths: list[RoutingPathItem]


class TopQueryItem(BaseModel):
    question: str
    count: int


class PerformanceStatsResponse(BaseModel):
    p50_total_time_ms: float
    p95_total_time_ms: float
    p99_total_time_ms: float
    averages: dict[str, float | None] = Field(default_factory=dict)
