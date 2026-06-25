from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class BusinessVerbDefinition(BaseModel):
    verb_id: str
    category: str
    aliases: list[str] = Field(default_factory=list)
    enabled: bool = True


class BusinessObjectDefinition(BaseModel):
    object_id: str
    aliases: list[str] = Field(default_factory=list)
    eko_sections: list[str] = Field(default_factory=list)
    ero_sections: list[str] = Field(default_factory=list)


class BusinessContextDefinition(BaseModel):
    context_id: str
    aliases: list[str] = Field(default_factory=list)


class VerbCatalogResponse(BaseModel):
    version: str
    verbs: list[BusinessVerbDefinition]
    total: int
    enabled_count: int


class SemanticParseRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class DetectedVerb(BaseModel):
    verb_id: str
    category: str
    matched_text: str
    confidence: Decimal


class DetectedObject(BaseModel):
    object_id: str
    matched_text: str
    confidence: Decimal
    ambiguous: bool = False


class SemanticParseResult(BaseModel):
    schema_version: str
    original_question: str
    normalized_question: str
    business_verb: DetectedVerb | None = None
    business_objects: list[DetectedObject] = Field(default_factory=list)
    business_context: list[str] = Field(default_factory=list)
    business_scope: list[str] = Field(default_factory=list)
    business_time: list[str] = Field(default_factory=list)
    business_constraints: list[str] = Field(default_factory=list)
    entity_hints: list[str] = Field(default_factory=list)
    unknown_tokens: list[str] = Field(default_factory=list)
    confidence: Decimal
    parsed_at: datetime
    metadata: dict = Field(default_factory=dict)


class BusinessExecutionPlan(BaseModel):
    schema_version: str
    plan_id: str
    original_question: str
    detected_verb: str | None = None
    detected_objects: list[str] = Field(default_factory=list)
    detected_context: list[str] = Field(default_factory=list)
    detected_timeframe: list[str] = Field(default_factory=list)
    required_knowledge: list[str] = Field(default_factory=list)
    required_reasoning: list[str] = Field(default_factory=list)
    required_evidence: list[str] = Field(default_factory=list)
    execution_strategy: str
    confidence: Decimal
    entity_hints: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    incomplete: bool = False
    incompatible_strategy: bool = False
    planned_at: datetime
    metadata: dict = Field(default_factory=dict)


class SemanticPlanRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class SemanticStatisticsResponse(BaseModel):
    semantic_parses: int
    execution_plans: int
    verb_distribution: dict[str, int]
    average_semantic_confidence: float
    planner_success_rate: float
    unknown_verbs: int
