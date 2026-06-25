import uuid
from statistics import mean

from app.enterprise_decision.evidence_analyzer import EvidenceAnalyzer
from app.enterprise_decision.financial_analyzer import FinancialAnalyzer
from app.enterprise_decision.recommendation_engine import RecommendationEngine
from app.enterprise_decision.repository import DecisionContext
from app.enterprise_decision.schemas import (
    DecisionType,
    EnterpriseDecisionPackage,
    EvidenceItem,
    RecommendationItem,
)
from app.enterprise_decision.simulation_analyzer import SimulationAnalyzer


class InsufficientEvidenceError(ValueError):
    """Se lanza cuando no hay evidencia suficiente para emitir una recomendación."""


class EnterpriseDecisionEngine:
    def __init__(self) -> None:
        self._evidence = EvidenceAnalyzer()
        self._financial = FinancialAnalyzer()
        self._simulation = SimulationAnalyzer()
        self._recommendations = RecommendationEngine()

    def build_package(
        self,
        *,
        decision_type: DecisionType,
        context: DecisionContext,
    ) -> EnterpriseDecisionPackage:
        evidence = self._evidence.analyze(context)
        if not evidence:
            raise InsufficientEvidenceError(
                "No hay evidencia disponible para generar una recomendación ejecutiva."
            )

        main, alternatives, risks, opportunities = self._recommendations.build(
            decision_type, context, evidence
        )
        self._validate_recommendation_evidence(main)
        for alt in alternatives:
            self._validate_recommendation_evidence(alt, allow_empty_ids=True)

        financial_impact, scenarios = self._financial.analyze(context)
        findings = self._simulation.findings(context)
        if context.operational_queries > 0:
            findings.insert(
                0,
                f"Se analizaron {context.operational_queries} consultas operativas registradas.",
            )
        if context.eks_documents > 0:
            findings.append(f"Servicio de conocimiento con {context.eks_documents} documentos activos.")

        confidence = self._confidence_level(main, evidence)
        summary = self._executive_summary(decision_type, main, financial_impact, confidence)

        unique_sources = sorted(set(context.sources_used))
        limitations = list(context.limitations)
        if context.operational_queries == 0:
            limitations.append("Sin histórico operativo; proyecciones basadas en valores por defecto.")
        limitations.append("Recomendaciones generadas por reglas determinísticas; no utilizan LLM.")

        return EnterpriseDecisionPackage(
            package_id=f"edp-{uuid.uuid4().hex[:12]}",
            decision_type=decision_type.value,
            executive_summary=summary,
            findings=findings,
            evidence_used=evidence,
            scenarios_considered=scenarios,
            financial_impact=financial_impact,
            risks=risks,
            opportunities=opportunities,
            main_recommendation=main,
            alternative_recommendations=alternatives,
            confidence_level=confidence,
            limitations=limitations,
            sources_used=unique_sources,
        )

    @staticmethod
    def _validate_recommendation_evidence(
        recommendation: RecommendationItem,
        *,
        allow_empty_ids: bool = False,
    ) -> None:
        if not allow_empty_ids and not recommendation.evidence_ids:
            raise InsufficientEvidenceError(
                f"La recomendación '{recommendation.title}' carece de evidencia vinculada."
            )

    @staticmethod
    def _confidence_level(main: RecommendationItem, evidence: list[EvidenceItem]) -> float:
        linked = [item.confidence for item in evidence if item.evidence_id in main.evidence_ids]
        if not linked:
            linked = [item.confidence for item in evidence]
        values = linked or [main.confidence]
        return round(min(mean(values), 1.0), 4)

    @staticmethod
    def _executive_summary(
        decision_type: DecisionType,
        main: RecommendationItem,
        financial,
        confidence: float,
    ) -> str:
        return (
            f"Decisión de tipo {decision_type.value}: {main.title}. "
            f"{main.detail} Impacto mensual proyectado: ${financial.monthly_projection_usd:.4f} USD "
            f"con ahorro de ${financial.avoided_cost_usd:.4f} USD. "
            f"Confianza: {confidence * 100:.1f}%."
        )
