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
from app.capability_discovery.engine import CapabilityDiscoveryEngine
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
from app.services.hybrid_chat_router import HybridChatRouter
from app.services.semantic_intent_builder import SemanticIntentBuilder
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


def get_executive_reasoning_handler(
    orchestration_service: AIOrchestrationService = Depends(get_ai_orchestration_service),
):
    from app.ai_orchestration.schemas import ExecutiveGenerateRequest
    from app.schemas.hybrid_chat import HybridChatResult

    def handler(message: str) -> HybridChatResult:
        response = orchestration_service.generate(ExecutiveGenerateRequest(question=message))
        answer = orchestration_service.format_executive_answer(response)
        return HybridChatResult(
            handled_by="executive_reasoning",
            success=not response.hallucination_guard_triggered or bool(answer),
            answer=answer,
            metadata={
                "handled_by": "executive_reasoning",
                "provider": response.provider,
                "model": response.model,
                "confidence": float(response.confidence),
                "tokens_input": response.tokens_input,
                "tokens_output": response.tokens_output,
                "estimated_cost": response.estimated_cost,
                "hallucination_guard_triggered": response.hallucination_guard_triggered,
                "evidence_package_id": response.evidence_package_id,
            },
        )

    return handler


def get_hybrid_chat_router(
    metrics_session: Session = Depends(get_db),
    business_executor: BusinessQueryExecutor = Depends(get_business_query_executor),
    response_engine: BusinessQueryResponseEngine = Depends(get_business_query_response_engine),
    legacy_executor: QueryExecutor = Depends(get_query_executor),
    context_builder: BusinessContextBuilder = Depends(get_business_context_builder),
    response_generator: ResponseGenerator = Depends(get_response_generator),
    deterministic_engine: DeterministicResponseEngine = Depends(get_deterministic_response_engine),
    executive_reasoning_handler=Depends(get_executive_reasoning_handler),
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

    metrics_repository = PerformanceMetricsRepository(metrics_session)

    def top_questions_provider(limit: int) -> list[str]:
        return [
            item["question"]
            for item in metrics_repository.get_top_queries(limit=limit)
        ]

    guided_fallback_engine = GuidedFallbackEngine(
        top_questions_provider=top_questions_provider,
    )
    capability_discovery_engine = CapabilityDiscoveryEngine(
        top_questions_provider=top_questions_provider,
    )
    suggested_questions_engine = SuggestedQuestionsEngine(
        top_questions_provider=top_questions_provider,
    )

    return HybridChatRouter(
        SemanticIntentBuilder(),
        BusinessQueryPlanner(),
        business_executor,
        response_engine,
        legacy_delegate,
        conversation_memory_service=_conversation_memory_service,
        guided_fallback_engine=guided_fallback_engine,
        capability_discovery_engine=capability_discovery_engine,
        suggested_questions_engine=suggested_questions_engine,
        performance_tracker=PerformanceTracker(metrics_session),
        executive_reasoning_handler=executive_reasoning_handler,
    )


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
