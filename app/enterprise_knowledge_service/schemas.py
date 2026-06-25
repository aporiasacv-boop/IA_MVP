from datetime import datetime

from pydantic import BaseModel, Field


class KnowledgeDocument(BaseModel):
    id: str
    title: str
    category: str
    path: str
    content: str
    provider: str = "knowledge_pack"
    sections: dict[str, str] = Field(default_factory=dict)


class KnowledgeCategorySummary(BaseModel):
    category: str
    label: str
    count: int


class KnowledgeSearchResult(BaseModel):
    query: str
    total: int
    items: list[KnowledgeDocument]
    average_search_time_ms: float = 0.0


class KnowledgeCategoriesResponse(BaseModel):
    categories: list[KnowledgeCategorySummary]
    total_documents: int


class KnowledgeProviderInfo(BaseModel):
    id: str
    name: str
    status: str
    document_count: int = 0


class KnowledgeProvidersResponse(BaseModel):
    active: list[KnowledgeProviderInfo]
    planned: list[KnowledgeProviderInfo]


class CapabilitiesPayload(BaseModel):
    answer: str
    capabilities: list[str]
    examples: list[str]


class InstitutionalAnswer(BaseModel):
    answer: str
    source: str
    category: str
    match_type: str
    provider: str = "knowledge_pack"
    confidence: float = 1.0


class BusinessContextRequest(BaseModel):
  question: str
  canonical_id: int | None = None


class BusinessContextResponse(BaseModel):
    available: bool
    summary: str
    sources: list[str] = Field(default_factory=list)
    provider: str = "enterprise_knowledge_service"


class EnterpriseKnowledgeStatistics(BaseModel):
    total_documents: int
    documents_by_category: dict[str, int]
    faq_entries: int
    knowledge_requests: int
    knowledge_runtime_hits: int
    knowledge_runtime_misses: int
    knowledge_runtime_cache_hits: int
    knowledge_runtime_reload_time_ms: float
    knowledge_runtime_last_refresh: datetime | None
    provider_distribution: dict[str, int]
    cache_hit_rate: float
    cache_size: int
    average_search_time_ms: float
    knowledge_sources: list[str]


class EnterpriseKnowledgeHealthResponse(BaseModel):
    status: str
    cache_valid: bool
    total_documents: int
    cache_size: int
    cache_hit_rate: float
    last_refresh: datetime | None
    reload_time_ms: float
    active_providers: list[str]
