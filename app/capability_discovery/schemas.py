from pydantic import BaseModel, Field

from app.suggested_questions.schemas import SuggestedQuestionsResult


class CapabilityDiscoveryResult(BaseModel):
    success: bool
    answer: str
    capabilities: list[str]
    example_questions: list[str] = Field(default_factory=list)
    suggestions: SuggestedQuestionsResult | None = None
    metadata: dict = Field(default_factory=dict)
