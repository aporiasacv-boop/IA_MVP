from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from app.semantic_intent.schemas import BusinessExecutionPlan


class EvidenceItem(BaseModel):
    """Elemento de evidencia estructurado para consumo LLM/RAG."""

    key: str
    value: Any
    source: str
    evidence: dict = Field(default_factory=dict)
    confidence: Decimal
    timestamp: datetime


class EvidenceConfidence(BaseModel):
    average_confidence: Decimal
    plan_confidence: Decimal
    knowledge_confidence: Decimal | None = None
    reasoning_confidence: Decimal | None = None
    items_count: int


class EvidenceLimitation(BaseModel):
    code: str
    description: str
    severity: str
    source: str


class EnterpriseEvidencePackage(BaseModel):
    """Contrato oficial del EEP v1 — sin texto narrativo ni SQL."""

    schema_version: str
    package_id: str
    question: str
    execution_plan: BusinessExecutionPlan
    business_context: dict = Field(default_factory=dict)
    knowledge: list[EvidenceItem] = Field(default_factory=list)
    reasoning: list[EvidenceItem] = Field(default_factory=list)
    facts: list[EvidenceItem] = Field(default_factory=list)
    signals: list[EvidenceItem] = Field(default_factory=list)
    alerts: list[EvidenceItem] = Field(default_factory=list)
    recommendations: list[EvidenceItem] = Field(default_factory=list)
    evidence: list[dict] = Field(default_factory=list)
    limitations: list[EvidenceLimitation] = Field(default_factory=list)
    confidence: EvidenceConfidence
    metadata: dict = Field(default_factory=dict)


class EvidenceBuildRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    canonical_id: int | None = None


class EvidenceSchemaResponse(BaseModel):
    schema_id: str
    schema_version: str
    required_sections: list[str]
    evidence_item_fields: list[str]
    description: str


class EvidenceStatisticsResponse(BaseModel):
    evidence_packages_total: int
    average_package_size: float
    average_evidence_items: float
    average_confidence: float
    missing_evidence: int
    package_build_time: float
