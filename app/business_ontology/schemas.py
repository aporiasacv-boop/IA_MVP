from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class OntologyTypeItem(BaseModel):
    type_id: int
    concept_category: str
    type_code: str
    type_label: str
    description: str | None = None
    is_active: bool
    sort_order: int


class OntologyTypeListResponse(BaseModel):
    items: list[OntologyTypeItem]
    total: int


class ProfileSummaryItem(BaseModel):
    total_movements: int
    total_amount: Decimal
    debit_credit_ratio: Decimal | None = None
    dimensions_used: list[str] = Field(default_factory=list)
    profile_completeness: Decimal


class IdentitySummaryItem(BaseModel):
    canonical_id: int
    canonical_name: str
    primary_rfc: str | None = None
    normalized_name: str
    alias_count: int


class OntologyAssignmentItem(BaseModel):
    assignment_id: int
    canonical_id: int
    concept_category: str
    type_code: str
    type_label: str
    rule_code: str
    evidence_json: dict
    score: Decimal
    confidence: Decimal
    status: str
    created_at: datetime


class OntologyEntityView(BaseModel):
    identity: IdentitySummaryItem
    profile_summary: ProfileSummaryItem | None = None
    assignments: list[OntologyAssignmentItem] = Field(default_factory=list)
    top_suggestions: list[OntologyAssignmentItem] = Field(default_factory=list)


class OntologyListResponse(BaseModel):
    items: list[OntologyEntityView]
    total: int
    page: int
    page_size: int


class OntologyAssignmentListResponse(BaseModel):
    items: list[OntologyAssignmentItem]
    total: int
    page: int
    page_size: int


class OntologyStatisticsResponse(BaseModel):
    ontology_entities: int
    ontology_pending: int
    ontology_approved: int
    ontology_rejected: int
    ontology_rules: int
    ontology_types: int
    ontology_average_confidence: float
    entities_without_suggestions: int
    last_ontology_run: datetime | None = None


class OntologyGenerationResult(BaseModel):
    types_seeded: int
    rules_seeded: int
    suggestions_inserted: int
    suggestions_updated: int
    entities_processed: int
    generation_time_seconds: float
