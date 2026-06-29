from pydantic import BaseModel, Field


class ExecutiveAgendaItem(BaseModel):
    title: str
    summary: str
    justification: str
    priority: str
    expected_impact: str
    suggested_query: str
    action_label: str = "Analizar"


class ExecutiveAgenda(BaseModel):
    greeting: str
    items: list[ExecutiveAgendaItem] = Field(default_factory=list)


class AdvisorInput(BaseModel):
    dataset_summary: dict | None = None
    temporal_coverage: dict | None = None
    executive_insight: dict | None = None
    business_copilot_proposals: list[dict] = Field(default_factory=list)
    conversation_context: dict | None = None
    recent_queries: list[str] = Field(default_factory=list)
    financial_scenario: dict | None = None
    operational_report: dict | None = None
    last_query_type: str | None = None
    last_answer: str | None = None
    last_user_question: str | None = None
    period: str | None = None
    scenario: str | None = None


class ExecutiveAgendaResponse(BaseModel):
    agenda: ExecutiveAgenda
    advisor_generation_ms: float = 0.0
    advisor_provider: str | None = None
    advisor_model: str | None = None
    advisor_items: int = 0
    advisor_fallback_used: bool = False
