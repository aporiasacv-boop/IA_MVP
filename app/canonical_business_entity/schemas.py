from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class EntityAliasItem(BaseModel):
    entity_id: int
    entity_code: str
    entity_name: str
    source_column: str
    resolution_rule: str
    resolution_score: Decimal


class CanonicalEntityItem(BaseModel):
    canonical_id: int
    canonical_name: str
    normalized_name: str
    primary_rfc: str | None
    alias_count: int
    aliases: list[EntityAliasItem] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class CanonicalEntityListResponse(BaseModel):
    items: list[CanonicalEntityItem]
    total: int
    page: int
    page_size: int


class SuggestionEntityRef(BaseModel):
    entity_id: int
    entity_code: str
    entity_name: str
    source_column: str


class CanonicalSuggestionItem(BaseModel):
    suggestion_id: int
    source_entity: SuggestionEntityRef
    candidate_entity: SuggestionEntityRef
    rule_used: str
    score: Decimal
    status: str
    created_at: datetime


class CanonicalSuggestionListResponse(BaseModel):
    items: list[CanonicalSuggestionItem]
    total: int
    page: int
    page_size: int


class CanonicalStatisticsResponse(BaseModel):
    canonical_entities_total: int
    canonical_matches: int
    pending_matches: int
    automatic_suggestions: int
    commercial_entities_total: int
    resolved_entities: int
    unresolved_entities: int
    unresolved_pct: float
    orphan_entities: int
    last_suggestion_run: datetime | None = None


class SuggestionRunResult(BaseModel):
    singletons_created: int
    resolutions_created: int
    suggestions_inserted: int
    suggestions_updated: int
