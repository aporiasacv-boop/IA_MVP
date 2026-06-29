from pydantic import BaseModel, Field


class ExecutiveInsightPayload(BaseModel):
    executive_summary: str | None = None
    business_interpretation: str | None = None
    possible_risks: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    next_questions: list[str] = Field(default_factory=list)


class InsightGenerationMetrics(BaseModel):
    insight_generation_ms: float = 0.0
    provider: str | None = None
    model: str | None = None
    insight_generated: bool = False
    fallback_used: bool = False
