from pydantic import BaseModel, Field


class AuditOverviewResponse(BaseModel):
    total_requests: int
    total_successes: int
    total_failures: int
    business_pipeline_pct: float
    memory_pct: float
    clarification_pct: float
    capability_pct: float
    fallback_pct: float
    legacy_pct: float
    coverage_score: float
    coverage_gap_score: float


class CoverageGapItem(BaseModel):
    question: str
    count: int
    route: str


class TopRouteItem(BaseModel):
    route: str
    count: int
    percentage: float


class TopFailureItem(BaseModel):
    question: str
    route: str
    frequency: int


class AdoptionMetricsResponse(BaseModel):
    suggested_questions_usage: int
    conversation_memory_usage: int
    slot_clarification_usage: int
    capability_discovery_usage: int


class TopDomainItem(BaseModel):
    domain: str
    count: int


class DomainFallbackMetricsResponse(BaseModel):
    domain_detected: str | None = None
    domain_fallback_hits: int = 0
    domain_fallback_misses: int = 0
    top_domains: list[TopDomainItem] = Field(default_factory=list)


class AuditReportResponse(BaseModel):
    overview: AuditOverviewResponse
    domain_fallback: DomainFallbackMetricsResponse
    generated_at: str


class CoverageGapsExportResponse(BaseModel):
    items: list[CoverageGapItem] = Field(default_factory=list)
    coverage_gap_score: float
    exported_at: str
