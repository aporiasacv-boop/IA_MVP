from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class ReasoningConclusion(BaseModel):
    """Conclusión empresarial determinística con trazabilidad XAI."""

    key: str
    value: Any
    rule_code: str
    evidence: dict = Field(default_factory=dict)
    confidence: Decimal
    severity: str
    computed_at: datetime


class ReasoningConfidence(BaseModel):
    average_confidence: Decimal
    conclusions_count: int
    rules_executed: int
    items: list[ReasoningConclusion] = Field(default_factory=list)


class EnterpriseReasoningObjectSchema(BaseModel):
    """Contrato oficial del ERO v1."""

    schema_version: str
    canonical_id: int
    findings: list[ReasoningConclusion] = Field(default_factory=list)
    signals: list[ReasoningConclusion] = Field(default_factory=list)
    alerts: list[ReasoningConclusion] = Field(default_factory=list)
    risks: list[ReasoningConclusion] = Field(default_factory=list)
    opportunities: list[ReasoningConclusion] = Field(default_factory=list)
    recommendations: list[ReasoningConclusion] = Field(default_factory=list)
    evidence: list[dict] = Field(default_factory=list)
    confidence: ReasoningConfidence
    metadata: dict = Field(default_factory=dict)


class ReasoningRuleDefinition(BaseModel):
    rule_code: str
    conclusion_type: str
    key: str
    value: Any = None
    value_from: str = "static"
    value_ref: str | None = None
    conditions: dict = Field(default_factory=dict)
    severity: str = "medium"
    confidence: Decimal = Decimal("0.8000")
    enabled: bool = True
    incompatible_with: list[str] = Field(default_factory=list)
    pack_id: str = ""
    description: str = ""


class ReasoningRulePack(BaseModel):
    pack_id: str
    version: str
    rules: list[ReasoningRuleDefinition]


class ReasoningObjectListItem(BaseModel):
    reasoning_id: int
    canonical_id: int
    canonical_name: str
    average_confidence: Decimal
    findings_count: int
    alerts_count: int
    recommendations_count: int
    built_at: datetime


class ReasoningObjectListResponse(BaseModel):
    items: list[ReasoningObjectListItem]
    total: int
    page: int
    page_size: int


class ReasoningStatisticsResponse(BaseModel):
    reasoning_objects_total: int
    knowledge_objects_total: int
    reasoning_rules_executed: int
    average_reasoning_confidence: float
    average_findings: float
    average_alerts: float
    average_recommendations: float
    last_reasoning_refresh: datetime | None = None
    incomplete_objects: int


class ReasoningRulesResponse(BaseModel):
    packs: list[ReasoningRulePack]
    total_rules: int
    enabled_rules: int


class ReasoningBuildResult(BaseModel):
    objects_upserted: int
    objects_created: int
    objects_updated: int
    entities_processed: int
    rules_executed: int
    build_time_seconds: float
