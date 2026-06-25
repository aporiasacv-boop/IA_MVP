from enum import StrEnum

from pydantic import BaseModel, Field


class DecisionType(StrEnum):
    PROVEEDOR_IA = "proveedor_ia"
    ESCENARIO = "escenario"
    INFRAESTRUCTURA = "infraestructura"
    ESTRATEGIA_DESPLIEGUE = "estrategia_despliegue"
    OPTIMIZACION_COSTOS = "optimizacion_costos"
    OPTIMIZACION_IA = "optimizacion_ia"
    OPTIMIZACION_PIPELINE = "optimizacion_pipeline"


class EvidenceItem(BaseModel):
    evidence_id: str
    source: str
    category: str
    metric: str
    value: str
    confidence: float = Field(ge=0.0, le=1.0)
    rule: str | None = None


class FinancialImpact(BaseModel):
    cost_usd: float = 0.0
    cost_mxn: float = 0.0
    avoided_cost_usd: float = 0.0
    roi_pct: float = 0.0
    llm_avoidance_rate: float = 0.0
    monthly_projection_usd: float = 0.0


class ScenarioConsidered(BaseModel):
    scenario_id: str
    scenario_name: str
    cost_usd: float
    avoided_cost_usd: float
    llm_avoidance_rate: float


class RecommendationItem(BaseModel):
    title: str
    detail: str
    decision_type: str
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class EnterpriseDecisionPackage(BaseModel):
    package_id: str
    decision_type: str
    executive_summary: str
    findings: list[str]
    evidence_used: list[EvidenceItem]
    scenarios_considered: list[ScenarioConsidered]
    financial_impact: FinancialImpact
    risks: list[str]
    opportunities: list[str]
    main_recommendation: RecommendationItem
    alternative_recommendations: list[RecommendationItem]
    confidence_level: float = Field(ge=0.0, le=1.0)
    limitations: list[str]
    sources_used: list[str]


class DecisionRecommendRequest(BaseModel):
    decision_type: DecisionType = DecisionType.PROVEEDOR_IA
    scenario_id: str = "piloto"
    question: str | None = None


class DecisionSchemaResponse(BaseModel):
    schema_id: str = "enterprise_decision_package_v1"
    schema_version: str = "1.0.0"
    decision_types: list[str]
    required_sections: list[str]
    description: str


class DecisionStatisticsResponse(BaseModel):
    decision_requests: int
    recommendation_types: dict[str, int]
    average_confidence: float
    average_financial_impact: float
    decision_sources: list[str]


class DecisionHealthResponse(BaseModel):
    status: str
    available_sources: list[str]
    missing_sources: list[str]
