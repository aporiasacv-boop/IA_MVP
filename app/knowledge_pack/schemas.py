from pydantic import BaseModel, Field


class KnowledgePackItem(BaseModel):
    id: str
    title: str
    category: str
    path: str
    content: str
    sections: dict[str, str] = Field(default_factory=dict)


class KnowledgePackListResponse(BaseModel):
    category: str
    total: int
    items: list[KnowledgePackItem]


class KnowledgePackSearchResponse(BaseModel):
    query: str
    total: int
    items: list[KnowledgePackItem]
