from datetime import datetime

from pydantic import BaseModel, Field


class KnowledgeDocument(BaseModel):
    id: str
    title: str
    category: str
    path: str
    content: str
    sections: dict[str, str] = Field(default_factory=dict)


class KnowledgeCategorySummary(BaseModel):
    category: str
    label: str
    count: int


class KnowledgeSearchResult(BaseModel):
    query: str
    total: int
    items: list[KnowledgeDocument]


class KnowledgeCategoriesResponse(BaseModel):
    categories: list[KnowledgeCategorySummary]
    total_documents: int


class KnowledgeRuntimeStatistics(BaseModel):
    total_documents: int
    documents_by_category: dict[str, int]
    faq_entries: int
    knowledge_runtime_hits: int
    knowledge_runtime_misses: int
    knowledge_runtime_cache_hits: int
    knowledge_runtime_reload_time_ms: float
    knowledge_runtime_last_refresh: datetime | None


class KnowledgeRuntimeHealthResponse(BaseModel):
    status: str
    pack_root_exists: bool
    total_documents: int
    last_refresh: datetime | None
    cache_valid: bool


class InstitutionalAnswer(BaseModel):
    answer: str
    source: str
    category: str
    match_type: str
    confidence: float = 1.0
