from app.business_analytics.constants import ROUTE_FIELDS
from app.business_analytics.financial_service import FinancialAnalyticsService
from app.business_analytics.repository import BusinessAnalyticsRepository
from app.business_analytics.schemas import (
    CoverageAnalyticsResponse,
    CoverageReportResponse,
    PerformanceAnalyticsResponse,
    TopQueryAnalyticsItem,
    TopRouteItem,
)
from app.business_entity_master.metrics import BusinessEntityMasterMetrics
from app.business_entity_master.repository import BusinessEntityMasterRepository
from app.business_ontology.metrics import BusinessOntologyMetrics
from app.business_ontology.repository import BusinessOntologyRepository
from app.business_entity_profile.metrics import EntityProfileMetrics
from app.business_entity_profile.repository import BusinessEntityProfileRepository
from app.enterprise_knowledge.metrics import EnterpriseKnowledgeMetrics
from app.enterprise_knowledge.repository import EnterpriseKnowledgeRepository
from app.evidence_package.metrics import EvidencePackageMetrics
from app.ai_orchestration.metrics import LLMOrchestrationMetrics
from app.enterprise_knowledge_service.metrics import get_enterprise_knowledge_metrics
from app.enterprise_knowledge_service.repository.repository import KnowledgeRepository
from app.semantic_intent.metrics import SemanticIntentMetrics
from app.enterprise_reasoning.metrics import EnterpriseReasoningMetrics
from app.enterprise_reasoning.repository import EnterpriseReasoningRepository
from app.canonical_business_entity.metrics import CanonicalEntityMetrics
from app.canonical_business_entity.repository import CanonicalBusinessEntityRepository


def _pct(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((count / total) * 100, 2)


class BusinessAnalyticsService:
    def __init__(
        self,
        repository: BusinessAnalyticsRepository,
        entity_repository: BusinessEntityMasterRepository | None = None,
        canonical_repository: CanonicalBusinessEntityRepository | None = None,
        profile_repository: BusinessEntityProfileRepository | None = None,
        ontology_repository: BusinessOntologyRepository | None = None,
        knowledge_repository: EnterpriseKnowledgeRepository | None = None,
        reasoning_repository: EnterpriseReasoningRepository | None = None,
    ) -> None:
        self._repository = repository
        self._financial = FinancialAnalyticsService(repository)
        self._entity_repository = entity_repository
        self._canonical_repository = canonical_repository
        self._profile_repository = profile_repository
        self._ontology_repository = ontology_repository
        self._knowledge_repository = knowledge_repository
        self._reasoning_repository = reasoning_repository

    def get_coverage(self) -> CoverageAnalyticsResponse:
        counts = self._repository.get_route_counts()
        total = counts["total_requests"]
        return CoverageAnalyticsResponse(
            total_requests=total,
            business_pipeline=counts["business_pipeline"],
            slot_clarification=counts["slot_clarification"],
            conversation_memory=counts["conversation_memory"],
            capability_discovery=counts["capability_discovery"],
            guided_fallback=counts["guided_fallback"],
            legacy_chat=counts["legacy_chat"],
            business_pipeline_pct=_pct(counts["business_pipeline"], total),
            slot_clarification_pct=_pct(counts["slot_clarification"], total),
            conversation_memory_pct=_pct(counts["conversation_memory"], total),
            capability_discovery_pct=_pct(counts["capability_discovery"], total),
            guided_fallback_pct=_pct(counts["guided_fallback"], total),
            legacy_chat_pct=_pct(counts["legacy_chat"], total),
        )

    def get_performance(self) -> PerformanceAnalyticsResponse:
        stats = self._repository.get_performance_percentiles()
        return PerformanceAnalyticsResponse(
            p50_ms=round(stats["p50_ms"], 4),
            p95_ms=round(stats["p95_ms"], 4),
            p99_ms=round(stats["p99_ms"], 4),
            avg_intent_ms=round(stats["avg_intent_ms"], 4),
            avg_planner_ms=round(stats["avg_planner_ms"], 4),
            avg_executor_ms=round(stats["avg_executor_ms"], 4),
            avg_response_ms=round(stats["avg_response_ms"], 4),
            avg_total_ms=round(stats["avg_total_ms"], 4),
        )

    def get_financial(self):
        return self._financial.get_financial_metrics()

    def get_top_queries(self, *, limit: int = 20) -> list[TopQueryAnalyticsItem]:
        rows = self._repository.get_top_queries_with_routes(limit=limit)
        return [TopQueryAnalyticsItem(**row) for row in rows]

    def get_report(self, *, route_limit: int = 10) -> CoverageReportResponse:
        financial = self._financial.get_financial_metrics()
        success_rate = round(self._repository.get_success_rate(), 4)
        top_routes = [
            TopRouteItem(
                handled_by=row["handled_by"],
                query_type=row["query_type"],
                count=row["count"],
                success_rate=row["success_rate"],
            )
            for row in self._repository.get_top_routes(limit=route_limit)
        ]
        deterministic_rate = financial.ai_avoidance_rate
        legacy_rate = financial.legacy_dependency_rate
        coverage_score = round(deterministic_rate * success_rate * 100, 2)
        entity_metrics = self._entity_metrics()
        canonical_metrics = self._canonical_metrics()
        profile_metrics = self._profile_metrics()
        ontology_metrics = self._ontology_metrics()
        knowledge_metrics = self._knowledge_metrics()
        reasoning_metrics = self._reasoning_metrics()
        semantic_metrics = SemanticIntentMetrics.snapshot()
        evidence_metrics = EvidencePackageMetrics.snapshot()
        llm_metrics = LLMOrchestrationMetrics.snapshot()
        eks_metrics = get_enterprise_knowledge_metrics()
        eks_repository = KnowledgeRepository()
        eks_metrics.set_provider_distribution(eks_repository.provider_distribution())
        return CoverageReportResponse(
            coverage_score=min(max(coverage_score, 0.0), 100.0),
            success_rate=success_rate,
            deterministic_rate=deterministic_rate,
            legacy_rate=legacy_rate,
            top_routes=top_routes,
            business_entities_total=entity_metrics["business_entities_total"],
            business_entities_loaded=entity_metrics["business_entities_loaded"],
            duplicated_entities=entity_metrics["duplicated_entities"],
            last_entity_refresh=entity_metrics["last_entity_refresh"],
            canonical_entities_total=canonical_metrics["canonical_entities_total"],
            canonical_matches=canonical_metrics["canonical_matches"],
            pending_matches=canonical_metrics["pending_matches"],
            automatic_suggestions=canonical_metrics["automatic_suggestions"],
            entity_profiles_total=profile_metrics["entity_profiles_total"],
            average_profile_completeness=profile_metrics["average_profile_completeness"],
            profile_generation_time=profile_metrics["profile_generation_time"],
            last_profile_refresh=profile_metrics["last_profile_refresh"],
            ontology_entities=ontology_metrics["ontology_entities"],
            ontology_pending=ontology_metrics["ontology_pending"],
            ontology_approved=ontology_metrics["ontology_approved"],
            ontology_rules=ontology_metrics["ontology_rules"],
            ontology_average_confidence=ontology_metrics["ontology_average_confidence"],
            knowledge_objects_total=knowledge_metrics["knowledge_objects_total"],
            knowledge_build_time=knowledge_metrics["knowledge_build_time"],
            knowledge_average_completeness=knowledge_metrics["knowledge_average_completeness"],
            knowledge_average_confidence=knowledge_metrics["knowledge_average_confidence"],
            knowledge_last_refresh=knowledge_metrics["knowledge_last_refresh"],
            reasoning_objects_total=reasoning_metrics["reasoning_objects_total"],
            reasoning_rules_executed=reasoning_metrics["reasoning_rules_executed"],
            average_reasoning_confidence=reasoning_metrics["average_reasoning_confidence"],
            average_findings=reasoning_metrics["average_findings"],
            average_alerts=reasoning_metrics["average_alerts"],
            average_recommendations=reasoning_metrics["average_recommendations"],
            last_reasoning_refresh=reasoning_metrics["last_reasoning_refresh"],
            semantic_parses=semantic_metrics["semantic_parses"],
            execution_plans=semantic_metrics["execution_plans"],
            verb_distribution=semantic_metrics["verb_distribution"],
            average_semantic_confidence=semantic_metrics["average_semantic_confidence"],
            planner_success_rate=semantic_metrics["planner_success_rate"],
            unknown_verbs=semantic_metrics["unknown_verbs"],
            evidence_packages_total=evidence_metrics["evidence_packages_total"],
            average_package_size=evidence_metrics["average_package_size"],
            average_evidence_items=evidence_metrics["average_evidence_items"],
            average_evidence_confidence=evidence_metrics["average_evidence_confidence"],
            missing_evidence=evidence_metrics["missing_evidence"],
            package_build_time=evidence_metrics["package_build_time"],
            llm_requests=llm_metrics["llm_requests"],
            provider_distribution=llm_metrics["provider_distribution"],
            tokens_input=llm_metrics["tokens_input"],
            tokens_output=llm_metrics["tokens_output"],
            estimated_llm_cost=llm_metrics["estimated_cost"],
            average_llm_latency=llm_metrics["average_latency"],
            average_cost_per_question=llm_metrics["average_cost_per_question"],
            hallucination_guard_triggered=llm_metrics["hallucination_guard_triggered"],
            llm_fallbacks=llm_metrics["llm_fallbacks"],
            knowledge_runtime_hits=eks_metrics.hits,
            knowledge_runtime_misses=eks_metrics.misses,
            knowledge_runtime_cache_hits=eks_metrics.cache_hits,
            knowledge_runtime_reload_time=eks_metrics.reload_time_ms,
            knowledge_runtime_last_refresh=eks_metrics.last_refresh,
            knowledge_runtime_documents=len(eks_repository.all_documents()),
            knowledge_requests=eks_metrics.knowledge_requests,
            knowledge_provider_distribution=eks_metrics.provider_distribution,
            cache_hit_rate=eks_metrics.cache_hit_rate,
            cache_size=eks_metrics.cache_size,
            average_search_time=eks_metrics.average_search_time_ms,
            knowledge_sources=list(eks_metrics.provider_distribution.keys()),
        )

    def _entity_metrics(self) -> dict:
        if self._entity_repository is None:
            return BusinessEntityMasterMetrics.snapshot(total=0)
        try:
            total = self._entity_repository.count_all()
            return BusinessEntityMasterMetrics.snapshot(total=total)
        except Exception:
            return BusinessEntityMasterMetrics.snapshot(total=0)

    def _canonical_metrics(self) -> dict:
        if self._canonical_repository is None:
            return CanonicalEntityMetrics.snapshot()
        try:
            return {
                "canonical_entities_total": self._canonical_repository.count_canonical(),
                "canonical_matches": self._canonical_repository.count_canonical_matches(),
                "pending_matches": self._canonical_repository.count_pending_suggestions(),
                "automatic_suggestions": self._canonical_repository.count_automatic_suggestions(),
            }
        except Exception:
            return CanonicalEntityMetrics.snapshot()

    def _profile_metrics(self) -> dict:
        if self._profile_repository is None:
            return EntityProfileMetrics.snapshot()
        try:
            return {
                "entity_profiles_total": self._profile_repository.count_profiles(),
                "average_profile_completeness": self._profile_repository.average_profile_completeness(),
                "profile_generation_time": EntityProfileMetrics.profile_generation_time,
                "last_profile_refresh": self._profile_repository.get_last_refresh()
                or EntityProfileMetrics.last_profile_refresh,
            }
        except Exception:
            return EntityProfileMetrics.snapshot()

    def _ontology_metrics(self) -> dict:
        if self._ontology_repository is None:
            return BusinessOntologyMetrics.snapshot()
        try:
            return {
                "ontology_entities": self._ontology_repository.count_entities_with_assignments(),
                "ontology_pending": self._ontology_repository.count_assignments(status="pending"),
                "ontology_approved": self._ontology_repository.count_assignments(status="approved"),
                "ontology_rules": self._ontology_repository.count_rules(),
                "ontology_average_confidence": self._ontology_repository.average_confidence(),
            }
        except Exception:
            return BusinessOntologyMetrics.snapshot()

    def _knowledge_metrics(self) -> dict:
        if self._knowledge_repository is None:
            return EnterpriseKnowledgeMetrics.snapshot()
        try:
            return {
                "knowledge_objects_total": self._knowledge_repository.count_objects(),
                "knowledge_build_time": EnterpriseKnowledgeMetrics.knowledge_build_time,
                "knowledge_average_completeness": self._knowledge_repository.average_completeness(),
                "knowledge_average_confidence": self._knowledge_repository.average_confidence(),
                "knowledge_last_refresh": self._knowledge_repository.get_last_refresh()
                or EnterpriseKnowledgeMetrics.knowledge_last_refresh,
            }
        except Exception:
            return EnterpriseKnowledgeMetrics.snapshot()

    def _reasoning_metrics(self) -> dict:
        if self._reasoning_repository is None:
            return EnterpriseReasoningMetrics.snapshot()
        try:
            return {
                "reasoning_objects_total": self._reasoning_repository.count_objects(),
                "reasoning_rules_executed": EnterpriseReasoningMetrics.reasoning_rules_executed,
                "average_reasoning_confidence": self._reasoning_repository.average_confidence(),
                "average_findings": self._reasoning_repository.average_findings(),
                "average_alerts": self._reasoning_repository.average_alerts(),
                "average_recommendations": self._reasoning_repository.average_recommendations(),
                "last_reasoning_refresh": self._reasoning_repository.get_last_refresh()
                or EnterpriseReasoningMetrics.last_reasoning_refresh,
            }
        except Exception:
            return EnterpriseReasoningMetrics.snapshot()

    def validate_health(self) -> dict:
        counts = self._repository.get_route_counts()
        coverage = self.get_coverage()
        financial = self.get_financial()
        report = self.get_report()

        total = counts["total_requests"]
        route_sum = sum(counts[route] for route in ROUTE_FIELDS)
        if total < route_sum:
            raise ValueError("total_requests debe ser >= suma de rutas")

        pct_sum = round(
            coverage.business_pipeline_pct
            + coverage.slot_clarification_pct
            + coverage.conversation_memory_pct
            + coverage.capability_discovery_pct
            + coverage.guided_fallback_pct
            + coverage.legacy_chat_pct,
            2,
        )
        if total > 0 and abs(pct_sum - 100.0) > 0.5:
            raise ValueError(f"Porcentajes inconsistentes: {pct_sum}")

        if not 0.0 <= financial.ai_avoidance_rate <= 1.0:
            raise ValueError("ai_avoidance_rate fuera de rango")
        if not 0.0 <= report.coverage_score <= 100.0:
            raise ValueError("coverage_score fuera de rango")

        for field_name in (
            "estimated_gpt_cost",
            "estimated_claude_cost",
            "estimated_ollama_cost",
        ):
            if getattr(financial, field_name) < 0:
                raise ValueError(f"{field_name} no puede ser negativo")

        return {
            "total_requests": total,
            "route_sum": route_sum,
            "coverage_score": report.coverage_score,
            "ai_avoidance_rate": financial.ai_avoidance_rate,
        }
