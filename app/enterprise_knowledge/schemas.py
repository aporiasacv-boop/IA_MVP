from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class KnowledgeItem(BaseModel):
    """Elemento de conocimiento verificable con trazabilidad."""

    key: str
    value: Any
    source: str
    evidence: dict = Field(default_factory=dict)
    confidence: Decimal
    computed_at: datetime


class KnowledgeIdentity(BaseModel):
    canonical_id: int
    canonical_name: str
    normalized_name: str
    primary_rfc: str | None = None
    alias_count: int
    aliases: list[dict] = Field(default_factory=list)
    items: list[KnowledgeItem] = Field(default_factory=list)


class KnowledgeQuality(BaseModel):
    completeness: Decimal
    average_confidence: Decimal
    profile_completeness: Decimal | None = None
    has_profile: bool
    has_ontology: bool
    ontology_assignment_count: int
    items: list[KnowledgeItem] = Field(default_factory=list)


class EnterpriseKnowledgeObjectSchema(BaseModel):
    """Contrato oficial del EKO v1."""

    schema_version: str
    canonical_id: int
    identity: KnowledgeIdentity
    roles: list[KnowledgeItem] = Field(default_factory=list)
    nature: list[KnowledgeItem] = Field(default_factory=list)
    behaviors: list[KnowledgeItem] = Field(default_factory=list)
    facts: list[KnowledgeItem] = Field(default_factory=list)
    signals: list[KnowledgeItem] = Field(default_factory=list)
    alerts: list[KnowledgeItem] = Field(default_factory=list)
    patterns: list[KnowledgeItem] = Field(default_factory=list)
    relationships: list[KnowledgeItem] = Field(default_factory=list)
    quality: KnowledgeQuality
    evidence: list[dict] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class KnowledgeObjectListItem(BaseModel):
    knowledge_id: int
    canonical_id: int
    canonical_name: str
    completeness: Decimal
    average_confidence: Decimal
    built_at: datetime


class KnowledgeObjectListResponse(BaseModel):
    items: list[KnowledgeObjectListItem]
    total: int
    page: int
    page_size: int


class KnowledgeStatisticsResponse(BaseModel):
    knowledge_objects_total: int
    canonical_entities_total: int
    knowledge_build_time: float
    knowledge_average_completeness: float
    knowledge_average_confidence: float
    knowledge_last_refresh: datetime | None = None
    incomplete_objects: int


class KnowledgeSchemaResponse(BaseModel):
    schema_id: str
    schema_version: str
    required_sections: list[str]
    knowledge_item_fields: list[str]
    description: str


class KnowledgeBuildResult(BaseModel):
    objects_upserted: int
    objects_created: int
    objects_updated: int
    entities_processed: int
    build_time_seconds: float
