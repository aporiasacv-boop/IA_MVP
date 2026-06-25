from sqlalchemy.orm import Session

from app.business_entity_master.metrics import BusinessEntityMasterMetrics
from app.business_entity_master.repository import BusinessEntityMasterRepository
from app.enterprise_knowledge.metrics import EnterpriseKnowledgeMetrics
from app.enterprise_knowledge.repository import EnterpriseKnowledgeRepository
from app.enterprise_reasoning.metrics import EnterpriseReasoningMetrics
from app.enterprise_reasoning.repository import EnterpriseReasoningRepository
from app.semantic_intent.metrics import SemanticIntentMetrics
from app.evidence_package.metrics import EvidencePackageMetrics
from app.ai_orchestration.metrics import LLMOrchestrationMetrics
from app.business_ontology.metrics import BusinessOntologyMetrics
from app.business_ontology.repository import BusinessOntologyRepository
from app.business_entity_profile.metrics import EntityProfileMetrics
from app.business_entity_profile.repository import BusinessEntityProfileRepository
from app.canonical_business_entity.metrics import CanonicalEntityMetrics
from app.canonical_business_entity.repository import CanonicalBusinessEntityRepository
from app.capability_discovery.v2.metrics import CapabilityDiscoveryV2Metrics
from app.coverage_recovery.metrics import CoverageRecoveryMetricsService
from app.guided_fallback.v2.metrics import GuidedFallbackV2Metrics
from app.observability.metrics_repository import PerformanceMetricsRepository
from app.schemas.metrics import (
    MetricsSummaryResponse,
    PerformanceStatsResponse,
    RoutingMetricsResponse,
    TopQueryItem,
)


class MetricsService:
    def __init__(self, repository: PerformanceMetricsRepository) -> None:
        self._repository = repository

    def get_summary(self) -> MetricsSummaryResponse:
        summary = self._repository.get_summary()
        summary.update(CoverageRecoveryMetricsService.snapshot())
        summary.update(CapabilityDiscoveryV2Metrics.snapshot())
        domain_metrics = GuidedFallbackV2Metrics.snapshot()
        summary.update(
            {
                "domain_detected": domain_metrics["domain_detected"],
                "domain_fallback_hits": domain_metrics["domain_fallback_hits"],
                "domain_fallback_misses": domain_metrics["domain_fallback_misses"],
                "top_domains": domain_metrics["top_domains"],
            }
        )
        bem_repo = BusinessEntityMasterRepository(self._repository.session)
        try:
            entity_total = bem_repo.count_all()
        except Exception:
            entity_total = 0
        summary.update(BusinessEntityMasterMetrics.snapshot(total=entity_total))
        cbe_repo = CanonicalBusinessEntityRepository(self._repository.session)
        try:
            summary.update(
                {
                    "canonical_entities_total": cbe_repo.count_canonical(),
                    "canonical_matches": cbe_repo.count_canonical_matches(),
                    "pending_matches": cbe_repo.count_pending_suggestions(),
                    "automatic_suggestions": cbe_repo.count_automatic_suggestions(),
                }
            )
        except Exception:
            summary.update(CanonicalEntityMetrics.snapshot())
        bep_repo = BusinessEntityProfileRepository(self._repository.session)
        try:
            summary.update(
                {
                    "entity_profiles_total": bep_repo.count_profiles(),
                    "average_profile_completeness": bep_repo.average_profile_completeness(),
                    "profile_generation_time": EntityProfileMetrics.profile_generation_time,
                    "last_profile_refresh": bep_repo.get_last_refresh()
                    or EntityProfileMetrics.last_profile_refresh,
                }
            )
        except Exception:
            summary.update(EntityProfileMetrics.snapshot())
        bo_repo = BusinessOntologyRepository(self._repository.session)
        try:
            summary.update(
                {
                    "ontology_entities": bo_repo.count_entities_with_assignments(),
                    "ontology_pending": bo_repo.count_assignments(status="pending"),
                    "ontology_approved": bo_repo.count_assignments(status="approved"),
                    "ontology_rules": bo_repo.count_rules(),
                    "ontology_average_confidence": bo_repo.average_confidence(),
                }
            )
        except Exception:
            summary.update(BusinessOntologyMetrics.snapshot())
        eko_repo = EnterpriseKnowledgeRepository(self._repository.session)
        try:
            summary.update(
                {
                    "knowledge_objects_total": eko_repo.count_objects(),
                    "knowledge_build_time": EnterpriseKnowledgeMetrics.knowledge_build_time,
                    "knowledge_average_completeness": eko_repo.average_completeness(),
                    "knowledge_average_confidence": eko_repo.average_confidence(),
                    "knowledge_last_refresh": eko_repo.get_last_refresh()
                    or EnterpriseKnowledgeMetrics.knowledge_last_refresh,
                }
            )
        except Exception:
            summary.update(EnterpriseKnowledgeMetrics.snapshot())
        ero_repo = EnterpriseReasoningRepository(self._repository.session)
        try:
            summary.update(
                {
                    "reasoning_objects_total": ero_repo.count_objects(),
                    "reasoning_rules_executed": EnterpriseReasoningMetrics.reasoning_rules_executed,
                    "average_reasoning_confidence": ero_repo.average_confidence(),
                    "average_findings": ero_repo.average_findings(),
                    "average_alerts": ero_repo.average_alerts(),
                    "average_recommendations": ero_repo.average_recommendations(),
                    "last_reasoning_refresh": ero_repo.get_last_refresh()
                    or EnterpriseReasoningMetrics.last_reasoning_refresh,
                }
            )
        except Exception:
            summary.update(EnterpriseReasoningMetrics.snapshot())
        summary.update(SemanticIntentMetrics.snapshot())
        summary.update(EvidencePackageMetrics.snapshot())
        llm_snap = LLMOrchestrationMetrics.snapshot()
        summary.update(
            {
                "llm_requests": llm_snap["llm_requests"],
                "provider_distribution": llm_snap["provider_distribution"],
                "tokens_input": llm_snap["tokens_input"],
                "tokens_output": llm_snap["tokens_output"],
                "estimated_llm_cost": llm_snap["estimated_cost"],
                "average_llm_latency": llm_snap["average_latency"],
                "average_cost_per_question": llm_snap["average_cost_per_question"],
                "hallucination_guard_triggered": llm_snap["hallucination_guard_triggered"],
                "llm_fallbacks": llm_snap["llm_fallbacks"],
                "executive_reasoning_requests": llm_snap["llm_requests"],
            }
        )
        return MetricsSummaryResponse(**summary)

    def get_top_queries(self, limit: int = 10) -> list[TopQueryItem]:
        return [TopQueryItem(**item) for item in self._repository.get_top_queries(limit=limit)]

    def get_performance(self) -> PerformanceStatsResponse:
        return PerformanceStatsResponse(**self._repository.get_performance())

    def get_routing_metrics(self, *, path_limit: int = 10) -> RoutingMetricsResponse:
        return RoutingMetricsResponse(**self._repository.get_routing_metrics(path_limit=path_limit))


def build_metrics_service(session: Session) -> MetricsService:
    return MetricsService(PerformanceMetricsRepository(session))
