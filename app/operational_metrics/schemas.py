from datetime import datetime

from pydantic import BaseModel, Field


class OperationalQueryRecord(BaseModel):
    request_id: str
    timestamp: datetime
    session_id: str | None = None
    handled_by: str
    provider: str = "platform"
    model: str = ""
    user_id: str | None = None
    channel: str = "hybrid"
    query_type: str | None = None
    verb: str | None = None
    intent: str | None = None
    response_time_ms: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_tokens: int = 0
    token_source: str = "none"
    cache_hit: bool = False
    knowledge_hit: bool = False
    pipeline_hit: bool = False
    executive_reasoning: bool = False
    llm_used: bool = False
    llm_provider: str | None = None
    llm_model: str | None = None
    success: bool = True
    confidence: float = 0.0
    cost_usd: float = 0.0
    cost_mxn: float = 0.0
    avoided_cost_usd: float = 0.0


class CostBreakdownItem(BaseModel):
    dimension: str
    key: str
    requests: int
    cost_usd: float
    cost_mxn: float
    tokens: int = 0


class FinOpsOverviewResponse(BaseModel):
    total_queries: int
    total_cost_usd: float
    total_cost_mxn: float
    cost_today_usd: float
    cost_month_usd: float
    cost_year_projected_usd: float
    avg_cost_per_query_usd: float
    avg_cost_per_session_usd: float
    avg_cost_per_user_usd: float
    llm_queries: int
    deterministic_queries: int
    llm_avoidance_rate: float
    knowledge_avoidance_rate: float
    pipeline_avoidance_rate: float
    total_avoided_cost_usd: float
    accumulated_savings_usd: float
    real_token_queries: int
    estimated_token_queries: int
    real_cost_share: float


class FinOpsCostsResponse(BaseModel):
    by_query: list[CostBreakdownItem] = Field(default_factory=list)
    by_session: list[CostBreakdownItem] = Field(default_factory=list)
    by_user: list[CostBreakdownItem] = Field(default_factory=list)
    by_day: list[CostBreakdownItem] = Field(default_factory=list)
    by_month: list[CostBreakdownItem] = Field(default_factory=list)
    by_year: list[CostBreakdownItem] = Field(default_factory=list)
    by_channel: list[CostBreakdownItem] = Field(default_factory=list)
    by_handled_by: list[CostBreakdownItem] = Field(default_factory=list)
    by_query_type: list[CostBreakdownItem] = Field(default_factory=list)
    by_provider: list[CostBreakdownItem] = Field(default_factory=list)
    by_model: list[CostBreakdownItem] = Field(default_factory=list)
    by_llm: list[CostBreakdownItem] = Field(default_factory=list)


class ProviderComparisonItem(BaseModel):
    provider: str
    requests: int
    tokens_input: int
    tokens_output: int
    total_tokens: int
    cost_usd: float
    average_latency_ms: float
    participation_pct: float


class FinOpsProvidersResponse(BaseModel):
    providers: list[ProviderComparisonItem]
    total_requests: int


class ForecastScenarioItem(BaseModel):
    users: int
    estimated_queries: int
    cost_openai_usd: float
    cost_claude_usd: float
    cost_ollama_usd: float
    estimated_cpu_cores: float
    estimated_ram_gb: float
    estimated_gpu_gb: float
    estimated_tokens: int
    estimated_latency_ms: float


class FinOpsForecastResponse(BaseModel):
    scenarios: list[ForecastScenarioItem]
    assumptions: dict[str, str]


class SavingsByRouteItem(BaseModel):
    handled_by: str
    queries: int
    avoided_cost_usd: float
    share_pct: float


class FinOpsSavingsResponse(BaseModel):
    llm_avoidance_rate: float
    knowledge_avoidance_rate: float
    pipeline_avoidance_rate: float
    total_avoided_cost_usd: float
    accumulated_savings_usd: float
    by_route: list[SavingsByRouteItem]


class TrendPoint(BaseModel):
    period: str
    queries: int
    cost_usd: float
    avoided_cost_usd: float
    llm_queries: int
    avg_latency_ms: float


class FinOpsTrendsResponse(BaseModel):
    daily: list[TrendPoint]
    monthly: list[TrendPoint]


class FinOpsHealthResponse(BaseModel):
    status: str
    records_stored: int
    last_record_at: datetime | None
    real_token_ratio: float
    data_source: str
