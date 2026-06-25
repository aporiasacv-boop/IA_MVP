from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from app.evidence_package.schemas import EnterpriseEvidencePackage


class EvidenceCitation(BaseModel):
    key: str
    source: str
    confidence: Decimal | None = None


class LLMGenerateResult(BaseModel):
    text: str
    tokens_input: int = 0
    tokens_output: int = 0
    model: str = ""
    provider: str = ""


class ExecutiveResponse(BaseModel):
    executive_summary: str
    detailed_analysis: str
    confidence: Decimal
    citations: list[EvidenceCitation] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    provider: str
    model: str
    tokens_input: int
    tokens_output: int
    estimated_cost: float
    response_time: float
    hallucination_guard_triggered: bool = False
    evidence_package_id: str | None = None


class ExecutiveGenerateRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    canonical_id: int | None = None


class ExecutiveGenerateFromPackageRequest(BaseModel):
    evidence_package: EnterpriseEvidencePackage


class ExecutiveSchemaResponse(BaseModel):
    schema_id: str
    schema_version: str
    response_fields: list[str]
    supported_providers: list[str]
    description: str


class ProviderCostItem(BaseModel):
    provider: str
    requests: int
    tokens_input: int
    tokens_output: int
    estimated_cost: float
    average_latency: float


class AICostSummaryResponse(BaseModel):
    llm_requests: int
    provider_distribution: dict[str, int]
    tokens_input: int
    tokens_output: int
    estimated_cost: float
    average_latency: float
    average_cost_per_question: float
    hallucination_guard_triggered: int
    llm_fallbacks: int
    cost_by_provider: list[ProviderCostItem]
    daily_cost: float
    monthly_cost: float
    cost_per_user: dict[str, float] = Field(default_factory=dict)
    cost_per_query: float
    provider_comparison: list[ProviderCostItem] = Field(default_factory=list)


class OrchestrationStatisticsResponse(BaseModel):
    llm_requests: int
    provider_distribution: dict[str, int]
    tokens_input: int
    tokens_output: int
    estimated_cost: float
    average_latency: float
    average_cost_per_question: float
    hallucination_guard_triggered: int
    llm_fallbacks: int


class OrchestrationHealthResponse(BaseModel):
    status: str
    provider: str
    provider_healthy: bool
    issues: list[dict[str, Any]] = Field(default_factory=list)
