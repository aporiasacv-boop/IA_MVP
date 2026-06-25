from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session


@dataclass
class DecisionContext:
    sources_used: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    eks_documents: int = 0
    eks_categories: int = 0
    eko_objects: int = 0
    eko_completeness: float = 0.0
    eko_confidence: float = 0.0
    ero_objects: int = 0
    ero_confidence: float = 0.0
    eep_packages: int = 0
    eep_confidence: float = 0.0
    operational_queries: int = 0
    finops_overview: dict[str, Any] = field(default_factory=dict)
    finops_savings: dict[str, Any] = field(default_factory=dict)
    finops_providers: list[dict[str, Any]] = field(default_factory=list)
    simulation_comparison: dict[str, Any] = field(default_factory=dict)
    simulation_run: dict[str, Any] = field(default_factory=dict)
    simulation_recommendations: list[dict[str, Any]] = field(default_factory=list)
    historical_route_mix: dict[str, float] = field(default_factory=dict)


class EnterpriseDecisionRepository:
    """Recopila contexto de solo lectura desde servicios enterprise existentes."""

    def gather(self, *, session: Session | None = None, scenario_id: str = "piloto") -> DecisionContext:
        context = DecisionContext()
        self._load_eks(context)
        self._load_operational_finops(context)
        self._load_simulation(context, scenario_id)
        if session is not None:
            self._load_eko(context, session)
            self._load_ero(context, session)
            self._load_eep(context, session)
        else:
            context.limitations.append("EKO/ERO/EEP no consultados: sesión de base de datos no disponible.")
        return context

    @staticmethod
    def _load_eks(context: DecisionContext) -> None:
        from app.enterprise_knowledge_service.service import get_enterprise_knowledge_platform_service

        try:
            service = get_enterprise_knowledge_platform_service()
            categories = service.list_categories()
            context.eks_documents = categories.total_documents
            context.eks_categories = len(categories.categories)
            context.sources_used.append("enterprise_knowledge_service")
        except Exception:
            context.limitations.append("Enterprise Knowledge Service no disponible.")

    @staticmethod
    def _load_operational_finops(context: DecisionContext) -> None:
        from app.operational_metrics.service import get_operational_metrics_service

        try:
            service = get_operational_metrics_service()
            overview = service.overview()
            savings = service.savings()
            providers = service.providers()
            context.operational_queries = overview.total_queries
            context.finops_overview = overview.model_dump()
            context.finops_savings = savings.model_dump()
            context.finops_providers = [p.model_dump() for p in providers.providers if p.requests > 0]
            for route in savings.by_route:
                context.historical_route_mix[route.handled_by] = route.share_pct
            context.sources_used.extend(["operational_metrics", "finops"])
        except Exception:
            context.limitations.append("Operational Metrics / FinOps no disponible.")

    @staticmethod
    def _load_simulation(context: DecisionContext, scenario_id: str) -> None:
        from app.simulation_engine.schemas import SimulationScenarioInput
        from app.simulation_engine.service import get_simulation_engine_service

        try:
            service = get_simulation_engine_service()
            run = service.run(SimulationScenarioInput(scenario_id=scenario_id, name=scenario_id))
            comparison = service.comparison()
            recommendations = service.recommendations()
            context.simulation_run = run.model_dump()
            context.simulation_comparison = comparison.model_dump()
            context.simulation_recommendations = [r.model_dump() for r in recommendations.recommendations]
            context.sources_used.append("simulation_engine")
        except Exception:
            context.limitations.append("Simulation Engine no disponible.")

    @staticmethod
    def _load_eko(context: DecisionContext, session: Session) -> None:
        from app.enterprise_knowledge.repository import EnterpriseKnowledgeRepository
        from app.enterprise_knowledge.service import EnterpriseKnowledgeService

        try:
            stats = EnterpriseKnowledgeService(EnterpriseKnowledgeRepository(session)).get_statistics()
            context.eko_objects = stats.knowledge_objects_total
            context.eko_completeness = stats.knowledge_average_completeness
            context.eko_confidence = stats.knowledge_average_confidence
            context.sources_used.append("eko")
        except Exception:
            context.limitations.append("EKO no disponible.")

    @staticmethod
    def _load_ero(context: DecisionContext, session: Session) -> None:
        from app.enterprise_reasoning.repository import EnterpriseReasoningRepository
        from app.enterprise_reasoning.service import EnterpriseReasoningService

        try:
            stats = EnterpriseReasoningService(EnterpriseReasoningRepository(session)).get_statistics()
            context.ero_objects = stats.reasoning_objects_total
            context.ero_confidence = stats.average_reasoning_confidence
            context.sources_used.append("ero")
        except Exception:
            context.limitations.append("ERO no disponible.")

    @staticmethod
    def _load_eep(context: DecisionContext, session: Session) -> None:
        from app.evidence_package.repository import EvidencePackageRepository
        from app.evidence_package.service import EvidencePackageService

        try:
            stats = EvidencePackageService(EvidencePackageRepository(session)).get_statistics()
            context.eep_packages = stats.evidence_packages_total
            context.eep_confidence = stats.average_evidence_confidence
            context.sources_used.append("eep")
        except Exception:
            context.limitations.append("EEP no disponible.")
