from pydantic import BaseModel, Field


class RouteMix(BaseModel):
    business_pipeline_pct: float = 0.0
    knowledge_service_pct: float = 0.0
    conversation_memory_pct: float = 0.0
    executive_reasoning_pct: float = 0.0
    legacy_chat_pct: float = 0.0
    other_pct: float = 0.0


class SimulationBaseline(BaseModel):
    source: str = "defaults"
    total_historical_queries: int = 0
    route_mix: RouteMix = Field(default_factory=RouteMix)
    avg_input_tokens: float = 800.0
    avg_output_tokens: float = 400.0
    avg_latency_ms: float = 850.0
    latency_p50_ms: float = 850.0
    latency_p95_ms: float = 1200.0
    latency_p99_ms: float = 1800.0
    avg_avoided_cost_usd: float = 0.0
    llm_avoidance_rate: float = 0.0
    knowledge_avoidance_rate: float = 0.0
    pipeline_avoidance_rate: float = 0.0
    memory_avoidance_rate: float = 0.0
    provider_latency: dict[str, float] = Field(default_factory=dict)
    provider_cost_share: dict[str, float] = Field(default_factory=dict)


class SimulationScenarioInput(BaseModel):
    scenario_id: str = "custom"
    name: str = "Hipótesis Personalizada"
    users: int = Field(default=100, ge=1, le=100000)
    queries_per_user_day: float = Field(default=12.0, ge=0.1, le=500.0)
    business_pipeline_pct: float | None = Field(default=None, ge=0, le=100)
    knowledge_service_pct: float | None = Field(default=None, ge=0, le=100)
    conversation_memory_pct: float | None = Field(default=None, ge=0, le=100)
    executive_reasoning_pct: float | None = Field(default=None, ge=0, le=100)
    legacy_chat_pct: float | None = Field(default=None, ge=0, le=100)
    llm_provider: str = "openai"
    llm_model: str = ""
    cost_per_1k_input_tokens: float | None = None
    cost_per_1k_output_tokens: float | None = None
    concurrency: int = Field(default=10, ge=1, le=10000)
    peak_hours: int = Field(default=8, ge=1, le=24)
    working_days: int = Field(default=22, ge=1, le=31)


class SimulationMetricsResult(BaseModel):
    queries_per_day: int
    queries_per_month: int
    total_tokens: int
    cost_usd: float
    cost_mxn: float
    avoided_cost_usd: float
    llm_avoidance_rate: float
    knowledge_savings_usd: float
    pipeline_savings_usd: float
    memory_savings_usd: float
    avg_latency_ms: float
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    estimated_cpu_cores: float
    estimated_ram_gb: float
    estimated_gpu_gb: float
    route_mix: RouteMix
    roi_pct: float


class ProviderSimulationResult(BaseModel):
    provider: str
    cost_usd: float
    cost_mxn: float
    avg_latency_ms: float
    avoided_cost_usd: float
    roi_pct: float
    participation_pct: float


class SimulationRunResponse(BaseModel):
    scenario_id: str
    scenario_name: str
    baseline_source: str
    metrics: SimulationMetricsResult
    provider_comparison: list[ProviderSimulationResult]
    assumptions: dict[str, str]


class PredefinedScenario(BaseModel):
    id: str
    name: str
    description: str
    defaults: SimulationScenarioInput


class SimulationScenariosResponse(BaseModel):
    baseline: SimulationBaseline
    predefined: list[PredefinedScenario]


class SimulationComparisonResponse(BaseModel):
    scenario_name: str
    providers: list[ProviderSimulationResult]
    cheapest_provider: str
    fastest_provider: str
    best_roi_provider: str


class SimulationRecommendation(BaseModel):
    category: str
    title: str
    detail: str
    metric_value: str


class SimulationRecommendationsResponse(BaseModel):
    recommendations: list[SimulationRecommendation]
    based_on_queries: int
    baseline_source: str


class SimulationHealthResponse(BaseModel):
    status: str
    baseline_source: str
    historical_queries: int
    simulation_runs: int
