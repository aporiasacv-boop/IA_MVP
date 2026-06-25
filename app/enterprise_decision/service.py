from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.enterprise_decision.decision_engine import EnterpriseDecisionEngine, InsufficientEvidenceError
from app.enterprise_decision.health import build_decision_health
from app.enterprise_decision.metrics import get_enterprise_decision_metrics
from app.enterprise_decision.repository import EnterpriseDecisionRepository
from app.enterprise_decision.schemas import (
    DecisionHealthResponse,
    DecisionRecommendRequest,
    DecisionSchemaResponse,
    DecisionStatisticsResponse,
    DecisionType,
    EnterpriseDecisionPackage,
)


@dataclass
class EnterpriseDecisionService:
    repository: EnterpriseDecisionRepository = field(default_factory=EnterpriseDecisionRepository)
    engine: EnterpriseDecisionEngine = field(default_factory=EnterpriseDecisionEngine)

    def recommend(
        self,
        request: DecisionRecommendRequest,
        *,
        session: Session | None = None,
    ) -> EnterpriseDecisionPackage:
        context = self.repository.gather(session=session, scenario_id=request.scenario_id)
        package = self.engine.build_package(decision_type=request.decision_type, context=context)
        get_enterprise_decision_metrics().record(
            decision_type=request.decision_type.value,
            confidence=package.confidence_level,
            financial_impact=package.financial_impact.avoided_cost_usd,
            sources=package.sources_used,
        )
        return package

    def get_schema(self) -> DecisionSchemaResponse:
        return DecisionSchemaResponse(
            decision_types=[item.value for item in DecisionType],
            required_sections=[
                "executive_summary",
                "findings",
                "evidence_used",
                "scenarios_considered",
                "financial_impact",
                "risks",
                "opportunities",
                "main_recommendation",
                "alternative_recommendations",
                "confidence_level",
                "limitations",
                "sources_used",
            ],
            description="Paquete de decisión ejecutiva basado en evidencia determinística.",
        )

    def get_statistics(self) -> DecisionStatisticsResponse:
        return DecisionStatisticsResponse(**get_enterprise_decision_metrics().snapshot())

    def get_example(self, *, session: Session | None = None) -> EnterpriseDecisionPackage:
        try:
            return self.recommend(
                DecisionRecommendRequest(decision_type=DecisionType.PROVEEDOR_IA, scenario_id="piloto"),
                session=session,
            )
        except InsufficientEvidenceError:
            context = self.repository.gather(session=session, scenario_id="piloto")
            package = self.engine.build_package(decision_type=DecisionType.ESCENARIO, context=context)
            return package

    def health(self, *, session: Session | None = None) -> DecisionHealthResponse:
        context = self.repository.gather(session=session, scenario_id="piloto")
        return build_decision_health(context)


_service: EnterpriseDecisionService | None = None


def get_enterprise_decision_service() -> EnterpriseDecisionService:
    global _service
    if _service is None:
        _service = EnterpriseDecisionService()
    return _service


def reset_enterprise_decision_service() -> None:
    global _service
    _service = None
