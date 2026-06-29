from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.executive_summary_repository import ExecutiveSummaryRepository
from app.repositories.insights_repository import InsightsRepository
from app.repositories.metadata_repository import MetadataRepository
from app.repositories.query_executor.cliente_repository import ClienteRepository
from app.repositories.query_executor.proveedor_repository import ProveedorRepository
from app.repositories.query_executor.system_repository import SystemRepository
from app.services.analytics_service import AnalyticsService
from app.services.business_context_builder import BusinessContextBuilder
from app.services.deterministic_response_engine import DeterministicResponseEngine
from app.services.insights_engine import InsightsEngine
from app.services.metadata_service import MetadataService
from app.services.query_executor import QueryExecutor
from app.services.response_generator import ResponseGenerator
from app.query_executor.business_query_executor import BusinessQueryExecutor
from app.query_engine.query_planner import BusinessQueryPlanner
from app.response_engine.deterministic_response_engine import (
    DeterministicResponseEngine as BusinessQueryResponseEngine,
)

from app.business_analytics.repository import BusinessAnalyticsRepository
from app.business_analytics.service import BusinessAnalyticsService
from app.business_entity_master.repository import BusinessEntityMasterRepository
from app.business_entity_master.service import BusinessEntityMasterService
from app.enterprise_knowledge.repository import EnterpriseKnowledgeRepository
from app.enterprise_knowledge.service import EnterpriseKnowledgeService
from app.enterprise_reasoning.repository import EnterpriseReasoningRepository
from app.enterprise_reasoning.service import EnterpriseReasoningService
from app.semantic_intent.service import SemanticIntentService
from app.evidence_package.repository import EvidencePackageRepository
from app.evidence_package.service import EvidencePackageService
from app.ai_orchestration.executive_response_engine import ExecutiveResponseEngine
from app.ai_orchestration.providers.factory import create_llm_provider_with_fallback
from app.ai_orchestration.service import AIOrchestrationService
from app.knowledge_pack.service import BusinessKnowledgePackService
from app.business_knowledge.runtime import BusinessKnowledgeRuntime
from app.enterprise_knowledge_service.service import (
    EnterpriseKnowledgePlatformService,
    get_enterprise_knowledge_platform_service,
)
from app.operational_metrics.service import OperationalMetricsService, get_operational_metrics_service
from app.simulation_engine.service import SimulationEngineService, get_simulation_engine_service
from app.enterprise_decision.service import EnterpriseDecisionService, get_enterprise_decision_service
from app.business_ontology.repository import BusinessOntologyRepository
from app.business_ontology.service import BusinessOntologyService
from app.business_entity_profile.repository import BusinessEntityProfileRepository
from app.business_entity_profile.service import BusinessEntityProfileService
from app.canonical_business_entity.repository import CanonicalBusinessEntityRepository
from app.canonical_business_entity.service import CanonicalBusinessEntityService
from app.operational_audit.repository import OperationalAuditRepository
from app.operational_audit.service import OperationalAuditService
from app.conversation_memory.service import ConversationMemoryService
from app.guided_fallback.engine import GuidedFallbackEngine
from app.observability.metrics_repository import PerformanceMetricsRepository
from app.observability.metrics_service import MetricsService, build_metrics_service
from app.observability.performance_tracker import PerformanceTracker
from app.capabilities.business_pipeline_capability import BusinessPipelineCapability
from app.capabilities.business_resolution_capability import BusinessResolutionCapability
from app.capabilities.business_understanding_capability import BusinessUnderstandingCapability
from app.capabilities.executive_reasoning_capability import ExecutiveReasoningCapability
from app.capabilities.guided_fallback_capability import GuidedFallbackCapability
from app.capabilities.institutional_knowledge_capability import InstitutionalKnowledgeCapability
from app.capabilities.conversation_context_capability import ConversationContextCapability
from app.capabilities.conversational_enrichment_capability import ConversationalEnrichmentCapability
from app.capability_executor.executor import CapabilityExecutor
from app.capability_registry.registry import CapabilityRegistry
from app.execution_plan.plan import ExecutionPlan
from app.enterprise_runtime.runtime import EnterpriseRuntime
from app.conversation_ux.gateway import ConversationIntelligenceGateway
from app.conversation_ux.presenter import ConversationPresenter
from app.conversation_ux.response_generator import ConversationResponseGenerator
from app.enterprise_personality.engine import EnterprisePersonalityEngine
from app.reasoning_engine.engine import EnterpriseReasoningEngine
from app.reasoning_engine.governed_executor import GovernedRouteExecutor
from app.reasoning_engine.governor import ReasoningGovernor
from app.services.hybrid_chat_router import HybridChatRouter
from app.services.semantic_intent_builder import SemanticIntentBuilder
from app.slot_clarification.engine import SlotClarificationEngine
from app.suggested_questions.engine import SuggestedQuestionsEngine


def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_analytics_service(session: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(AnalyticsRepository(session))


def get_insights_engine(session: Session = Depends(get_db)) -> InsightsEngine:
    return InsightsEngine(InsightsRepository(session))


def get_metadata_service(session: Session = Depends(get_db)) -> MetadataService:
    return MetadataService(MetadataRepository(session))


def get_query_executor(
    session: Session = Depends(get_db),
    metadata_service: MetadataService = Depends(get_metadata_service),
) -> QueryExecutor:
    return QueryExecutor(
        AnalyticsService(AnalyticsRepository(session)),
        InsightsEngine(InsightsRepository(session)),
        metadata_service=metadata_service,
    )


def get_response_generator(
    metadata_service: MetadataService = Depends(get_metadata_service),
) -> ResponseGenerator:
    return ResponseGenerator(metadata_service=metadata_service)


def get_business_context_builder(
    session: Session = Depends(get_db),
) -> BusinessContextBuilder:
    return BusinessContextBuilder(
        AnalyticsService(AnalyticsRepository(session)),
        InsightsEngine(InsightsRepository(session)),
        MetadataService(MetadataRepository(session)),
    )


def get_deterministic_response_engine(
    session: Session = Depends(get_db),
) -> DeterministicResponseEngine:
    return DeterministicResponseEngine(
        executive_summary_repository=ExecutiveSummaryRepository(session),
        analytics_service=AnalyticsService(AnalyticsRepository(session)),
        insights_engine=InsightsEngine(InsightsRepository(session)),
        metadata_service=MetadataService(MetadataRepository(session)),
        insights_repository=InsightsRepository(session),
    )


def get_business_query_executor(
    session: Session = Depends(get_db),
) -> BusinessQueryExecutor:
    return BusinessQueryExecutor(
        ClienteRepository(session),
        ProveedorRepository(session),
        SystemRepository(session),
    )


def get_business_query_response_engine() -> BusinessQueryResponseEngine:
    return BusinessQueryResponseEngine()


_conversation_memory_service = ConversationMemoryService()


def get_conversation_memory_service() -> ConversationMemoryService:
    return _conversation_memory_service


def get_evidence_package_service(
    session: Session = Depends(get_db),
) -> EvidencePackageService:
    return EvidencePackageService(EvidencePackageRepository(session))


def get_ai_orchestration_service(
    session: Session = Depends(get_db),
) -> AIOrchestrationService:
    evidence_service = EvidencePackageService(EvidencePackageRepository(session))
    engine = ExecutiveResponseEngine(create_llm_provider_with_fallback())
    return AIOrchestrationService(evidence_service, engine)


def get_executive_reasoning_capability(
    orchestration_service: AIOrchestrationService = Depends(get_ai_orchestration_service),
) -> ExecutiveReasoningCapability:
    return ExecutiveReasoningCapability.from_orchestration_service(orchestration_service)


def _build_suggested_questions_engine(metrics_session: Session) -> SuggestedQuestionsEngine:
    metrics_repository = PerformanceMetricsRepository(metrics_session)

    def top_questions_provider(limit: int) -> list[str]:
        return [
            item["question"]
            for item in metrics_repository.get_top_queries(limit=limit)
        ]

    return SuggestedQuestionsEngine(top_questions_provider=top_questions_provider)


def get_conversation_context_capability() -> ConversationContextCapability:
    return ConversationContextCapability(
        conversation_memory_service=_conversation_memory_service,
    )


def get_business_understanding_capability() -> BusinessUnderstandingCapability:
    return BusinessUnderstandingCapability(
        SemanticIntentBuilder(),
        BusinessQueryPlanner(),
    )


def get_business_resolution_capability(
    business_executor: BusinessQueryExecutor = Depends(get_business_query_executor),
    response_engine: BusinessQueryResponseEngine = Depends(get_business_query_response_engine),
) -> BusinessResolutionCapability:
    return BusinessResolutionCapability(business_executor, response_engine)


def get_conversational_enrichment_capability(
    metrics_session: Session = Depends(get_db),
) -> ConversationalEnrichmentCapability:
    return ConversationalEnrichmentCapability(
        suggested_questions_engine=_build_suggested_questions_engine(metrics_session),
    )


def _top_questions_provider(metrics_session: Session):
    metrics_repository = PerformanceMetricsRepository(metrics_session)

    def provider(limit: int) -> list[str]:
        return [
            item["question"]
            for item in metrics_repository.get_top_queries(limit=limit)
        ]

    return provider


def get_guided_fallback_capability(
    metrics_session: Session = Depends(get_db),
) -> GuidedFallbackCapability:
    return GuidedFallbackCapability(
        GuidedFallbackEngine(top_questions_provider=_top_questions_provider(metrics_session)),
    )


def get_hybrid_chat_router(
    metrics_session: Session = Depends(get_db),
    legacy_executor: QueryExecutor = Depends(get_query_executor),
    context_builder: BusinessContextBuilder = Depends(get_business_context_builder),
    response_generator: ResponseGenerator = Depends(get_response_generator),
    deterministic_engine: DeterministicResponseEngine = Depends(get_deterministic_response_engine),
    conversation_context: ConversationContextCapability = Depends(
        get_conversation_context_capability
    ),
) -> HybridChatRouter:
    from app.api.routes.chat import chat as legacy_chat_handler
    from app.schemas.chat import ChatRequest

    def legacy_delegate(message: str):
        return legacy_chat_handler(
            ChatRequest(question=message),
            executor=legacy_executor,
            context_builder=context_builder,
            response_generator=response_generator,
            deterministic_engine=deterministic_engine,
        )

    def top_questions_provider(limit: int) -> list[str]:
        return _top_questions_provider(metrics_session)(limit)

    return HybridChatRouter(
        legacy_delegate,
        conversation_context=conversation_context,
        performance_tracker=PerformanceTracker(metrics_session),
    )


def get_execution_plan() -> ExecutionPlan:
    return ExecutionPlan.default_inquiry()


def get_institutional_knowledge_capability() -> InstitutionalKnowledgeCapability:
    return InstitutionalKnowledgeCapability()


def get_business_pipeline_capability(
    hybrid_router: HybridChatRouter = Depends(get_hybrid_chat_router),
    conversational_enrichment: ConversationalEnrichmentCapability = Depends(
        get_conversational_enrichment_capability
    ),
    conversation_context: ConversationContextCapability = Depends(
        get_conversation_context_capability
    ),
    business_understanding: BusinessUnderstandingCapability = Depends(
        get_business_understanding_capability
    ),
    business_resolution: BusinessResolutionCapability = Depends(
        get_business_resolution_capability
    ),
    institutional_knowledge: InstitutionalKnowledgeCapability = Depends(
        get_institutional_knowledge_capability
    ),
    executive_reasoning: ExecutiveReasoningCapability = Depends(
        get_executive_reasoning_capability
    ),
    guided_fallback: GuidedFallbackCapability = Depends(get_guided_fallback_capability),
) -> BusinessPipelineCapability:
    return BusinessPipelineCapability(
        hybrid_router,
        conversational_enrichment,
        conversation_context,
        business_understanding,
        business_resolution,
        institutional_knowledge,
        executive_reasoning,
        guided_fallback,
        slot_clarification_engine=SlotClarificationEngine(),
    )


def get_capability_registry(
    business_pipeline: BusinessPipelineCapability = Depends(get_business_pipeline_capability),
    conversational_enrichment: ConversationalEnrichmentCapability = Depends(
        get_conversational_enrichment_capability
    ),
) -> CapabilityRegistry:
    return CapabilityRegistry(
        business_pipeline=business_pipeline,
        conversational_enrichment=conversational_enrichment,
    )


def get_capability_executor(
    capability_registry: CapabilityRegistry = Depends(get_capability_registry),
) -> CapabilityExecutor:
    return CapabilityExecutor(capability_registry)


def get_enterprise_runtime(
    execution_plan: ExecutionPlan = Depends(get_execution_plan),
    capability_executor: CapabilityExecutor = Depends(get_capability_executor),
) -> EnterpriseRuntime:
    return EnterpriseRuntime(execution_plan, capability_executor)


def get_conversation_presenter(
    metadata_service: MetadataService = Depends(get_metadata_service),
) -> ConversationPresenter:
    return ConversationPresenter(
        knowledge_service=get_enterprise_knowledge_platform_service(),
        dataset_summary_provider=metadata_service.get_dataset_summary,
    )


def get_conversation_response_generator() -> ConversationResponseGenerator:
    return ConversationResponseGenerator(create_llm_provider_with_fallback())


def get_conversation_intelligence_gateway(
    conversation_presenter: ConversationPresenter = Depends(get_conversation_presenter),
) -> ConversationIntelligenceGateway:
    return ConversationIntelligenceGateway(conversation_presenter)


def get_enterprise_reasoning_engine() -> EnterpriseReasoningEngine:
    return EnterpriseReasoningEngine(create_llm_provider_with_fallback())


def get_reasoning_governor() -> ReasoningGovernor:
    return ReasoningGovernor()


def get_governed_route_executor(
    conversation_presenter: ConversationPresenter = Depends(get_conversation_presenter),
    institutional_knowledge: InstitutionalKnowledgeCapability = Depends(
        get_institutional_knowledge_capability
    ),
) -> GovernedRouteExecutor:
    return GovernedRouteExecutor(
        conversation_presenter=conversation_presenter,
        institutional_knowledge=institutional_knowledge,
        guided_fallback_engine=GuidedFallbackEngine(),
    )


def get_enterprise_personality_engine() -> EnterprisePersonalityEngine:
    return EnterprisePersonalityEngine()


def get_executive_insight_engine() -> "ExecutiveInsightEngine":
    from app.executive_insight.engine import ExecutiveInsightEngine

    return ExecutiveInsightEngine()


def get_executive_reasoning_v2_engine() -> "ExecutiveReasoningV2Engine":
    from app.executive_reasoning_v2.engine import ExecutiveReasoningV2Engine

    return ExecutiveReasoningV2Engine()


def get_business_copilot_engine() -> "BusinessCopilotEngine":
    from app.business_copilot.engine import BusinessCopilotEngine

    if not hasattr(get_business_copilot_engine, "_instance"):
        get_business_copilot_engine._instance = BusinessCopilotEngine(
            conversation_memory_service=get_conversation_memory_service(),
        )
    return get_business_copilot_engine._instance


def get_executive_advisor_engine() -> "ExecutiveAdvisorEngine":
    from app.executive_advisor.engine import ExecutiveAdvisorEngine

    if not hasattr(get_executive_advisor_engine, "_instance"):
        get_executive_advisor_engine._instance = ExecutiveAdvisorEngine()
    return get_executive_advisor_engine._instance


def get_metrics_service(session: Session = Depends(get_db)) -> MetricsService:
    return build_metrics_service(session)


def get_business_analytics_service(
    session: Session = Depends(get_db),
) -> BusinessAnalyticsService:
    return BusinessAnalyticsService(
        BusinessAnalyticsRepository(session),
        BusinessEntityMasterRepository(session),
        CanonicalBusinessEntityRepository(session),
        BusinessEntityProfileRepository(session),
        BusinessOntologyRepository(session),
        EnterpriseKnowledgeRepository(session),
        EnterpriseReasoningRepository(session),
    )


def get_executive_advisor_service(
    metadata_service: MetadataService = Depends(get_metadata_service),
    business_analytics_service: BusinessAnalyticsService = Depends(get_business_analytics_service),
):
    from app.executive_advisor.service import ExecutiveAdvisorService

    return ExecutiveAdvisorService(
        advisor_engine=get_executive_advisor_engine(),
        dataset_summary_provider=metadata_service.get_dataset_summary,
        top_queries_provider=lambda limit: [
            item.model_dump() for item in business_analytics_service.get_top_queries(limit)
        ],
        coverage_report_provider=lambda: business_analytics_service.get_report().model_dump(),
        conversation_memory_service=get_conversation_memory_service(),
    )


def get_capability_reasoning_audit():
    from app.capability_reasoning_audit.engine import CapabilityReasoningAudit

    return CapabilityReasoningAudit()


def get_capability_reasoner():
    from app.capability_reasoner.engine import CapabilityReasoner

    return CapabilityReasoner()


def get_capability_query_runner(
    enterprise_runtime=Depends(get_enterprise_runtime),
):
    from app.query_engine.query_catalog import QUERY_TYPE_EXAMPLE_QUESTIONS
    from app.query_engine.query_types import BusinessQueryType

    def run(capability_id: str, session_id: str | None):
        query_type = BusinessQueryType(capability_id)
        canonical_question = QUERY_TYPE_EXAMPLE_QUESTIONS[query_type]
        return enterprise_runtime.process_inquiry(canonical_question, session_id=session_id)

    return run


def get_capability_plan_executor(
    execute_capability=Depends(get_capability_query_runner),
):
    from app.capability_plan_executor.engine import CapabilityPlanExecutor

    return CapabilityPlanExecutor(execute_capability=execute_capability)


def get_enterprise_evidence_planner():
    from app.enterprise_evidence_planner.engine import EnterpriseEvidencePlanner

    return EnterpriseEvidencePlanner()


def get_enterprise_evidence_orchestrator(
    execute_capability=Depends(get_capability_query_runner),
):
    from app.enterprise_evidence_orchestrator.engine import EnterpriseEvidenceOrchestrator

    return EnterpriseEvidenceOrchestrator(execute_capability=execute_capability)


def get_operational_audit_service(
    session: Session = Depends(get_db),
) -> OperationalAuditService:
    return OperationalAuditService(OperationalAuditRepository(session))


def get_business_entity_master_service(
    session: Session = Depends(get_db),
) -> BusinessEntityMasterService:
    return BusinessEntityMasterService(BusinessEntityMasterRepository(session))


def get_canonical_business_entity_service(
    session: Session = Depends(get_db),
) -> CanonicalBusinessEntityService:
    return CanonicalBusinessEntityService(CanonicalBusinessEntityRepository(session))


def get_business_entity_profile_service(
    session: Session = Depends(get_db),
) -> BusinessEntityProfileService:
    return BusinessEntityProfileService(BusinessEntityProfileRepository(session))


def get_business_ontology_service(
    session: Session = Depends(get_db),
) -> BusinessOntologyService:
    return BusinessOntologyService(BusinessOntologyRepository(session))


def get_enterprise_knowledge_service(
    session: Session = Depends(get_db),
) -> EnterpriseKnowledgeService:
    return EnterpriseKnowledgeService(EnterpriseKnowledgeRepository(session))


def get_enterprise_reasoning_service(
    session: Session = Depends(get_db),
) -> EnterpriseReasoningService:
    return EnterpriseReasoningService(EnterpriseReasoningRepository(session))


def get_semantic_intent_service() -> SemanticIntentService:
    return SemanticIntentService()


def get_enterprise_knowledge_platform_service_dep() -> EnterpriseKnowledgePlatformService:
    return get_enterprise_knowledge_platform_service()


def get_operational_metrics_service_dep(
    session: Session = Depends(get_db),
) -> OperationalMetricsService:
    return get_operational_metrics_service(session)


def get_simulation_engine_service_dep() -> SimulationEngineService:
    return get_simulation_engine_service()


def get_enterprise_decision_service_dep() -> EnterpriseDecisionService:
    return get_enterprise_decision_service()


def get_business_knowledge_pack_service() -> BusinessKnowledgePackService:
    return BusinessKnowledgePackService()


def get_business_knowledge_runtime() -> BusinessKnowledgeRuntime:
    return BusinessKnowledgeRuntime()
