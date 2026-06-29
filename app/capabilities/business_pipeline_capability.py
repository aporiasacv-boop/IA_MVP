import time

from app.capabilities.business_pipeline_state import BusinessPipelineState
from app.capabilities.business_resolution_capability import BusinessResolutionCapability
from app.capabilities.business_understanding_capability import BusinessUnderstandingCapability
from app.capabilities.conversational_enrichment_capability import ConversationalEnrichmentCapability
from app.capabilities.conversation_context_capability import ConversationContextCapability
from app.capabilities.executive_reasoning_capability import ExecutiveReasoningCapability
from app.capabilities.guided_fallback_capability import GuidedFallbackCapability
from app.capabilities.institutional_knowledge_capability import InstitutionalKnowledgeCapability
from app.coverage_recovery.metrics import CoverageRecoveryMetricsService
from app.observability.performance_metrics import elapsed_ms
from app.query_engine.query_types import BusinessQueryType
from app.schemas.hybrid_chat import HybridChatResult
from app.services.hybrid_chat_router import HybridChatRouter
from app.slot_clarification.engine import SlotClarificationEngine
from app.slot_clarification.schemas import SlotClarificationResult


class BusinessPipelineCapability:
    """Orquesta el pipeline principal de negocio y delega el enrutamiento al router."""

    def __init__(
        self,
        hybrid_router: HybridChatRouter,
        conversational_enrichment: ConversationalEnrichmentCapability,
        conversation_context: ConversationContextCapability,
        business_understanding: BusinessUnderstandingCapability,
        business_resolution: BusinessResolutionCapability,
        institutional_knowledge: InstitutionalKnowledgeCapability,
        executive_reasoning: ExecutiveReasoningCapability,
        guided_fallback: GuidedFallbackCapability,
        slot_clarification_engine: SlotClarificationEngine | None = None,
    ) -> None:
        self._hybrid_router = hybrid_router
        self._conversational_enrichment = conversational_enrichment
        self._conversation_context = conversation_context
        self._business_understanding = business_understanding
        self._business_resolution = business_resolution
        self._institutional_knowledge = institutional_knowledge
        self._executive_reasoning = executive_reasoning
        self._guided_fallback = guided_fallback
        self._slot_clarification_engine = (
            slot_clarification_engine or SlotClarificationEngine()
        )

    def execute(self, message: str, session_id: str | None = None) -> HybridChatResult:
        pipeline_state = self._prepare_pipeline_state(message, session_id)
        institutional_result = self._resolve_institutional_if_needed(
            message,
            pipeline_state,
        )
        if institutional_result is not None:
            raw_result = institutional_result
            collector = None
        else:
            route_outcome = self._hybrid_router.route(
                message,
                pipeline_state=pipeline_state,
            )
            raw_result = route_outcome.result
            collector = route_outcome.collector
        enriched = self._conversational_enrichment.enrich(
            raw_result,
            context=pipeline_state.context,
        )
        CoverageRecoveryMetricsService.record_outcome(message, enriched)
        self._hybrid_router.finalize_observability(
            enriched,
            collector=collector,
        )
        return enriched

    def _resolve_institutional_if_needed(
        self,
        message: str,
        pipeline_state: BusinessPipelineState,
    ) -> HybridChatResult | None:
        understanding = pipeline_state.business_understanding
        if understanding is None:
            return None
        if understanding.result.query.query_type != BusinessQueryType.SYSTEM_CAPABILITIES:
            return None

        result = self._institutional_knowledge.resolve_system_capabilities(message)
        self._conversation_context.save_context(
            pipeline_state.session_id,
            pipeline_state.context,
        )
        return result

    def _prepare_pipeline_state(
        self,
        message: str,
        session_id: str | None,
    ) -> BusinessPipelineState:
        session_id, context = self._conversation_context.prepare_session(message, session_id)

        memory_started = time.perf_counter()
        memory_resolution = self._conversation_context.resolve(message, context)
        conversation_memory_stage_ms = elapsed_ms(memory_started)

        if memory_resolution is not None:
            self._conversation_context.record_memory_hit(memory_resolution)
        else:
            self._conversation_context.record_memory_miss_if_applicable(context)

        business_understanding = None
        slot_clarification: SlotClarificationResult | None = None
        slot_clarification_stage_ms: float | None = None
        business_resolution = None
        executive_reasoning = None
        guided_fallback = None

        if memory_resolution is not None:
            business_resolution = self._business_resolution.resolve(memory_resolution.query)
        else:
            business_understanding = self._business_understanding.understand(message)
            intent = business_understanding.result.intent
            query = business_understanding.result.query

            if query.query_type not in {
                BusinessQueryType.UNSUPPORTED,
                BusinessQueryType.SYSTEM_CAPABILITIES,
            }:
                clarification_started = time.perf_counter()
                clarification = self._slot_clarification_engine.resolve(intent, query)
                slot_clarification_stage_ms = elapsed_ms(clarification_started)
                if clarification is not None:
                    slot_clarification = clarification
                else:
                    business_resolution = self._business_resolution.resolve(query)
            elif query.query_type == BusinessQueryType.UNSUPPORTED:
                executive_reasoning = self._executive_reasoning.try_reason(message)
                if executive_reasoning is None:
                    guided_fallback = self._guided_fallback.try_fallback(
                        message,
                        intent,
                        query,
                        context,
                        session_id=session_id,
                    )

        return BusinessPipelineState(
            session_id=session_id,
            context=context,
            memory_resolution=memory_resolution,
            conversation_memory_stage_ms=conversation_memory_stage_ms,
            business_understanding=business_understanding,
            slot_clarification=slot_clarification,
            slot_clarification_stage_ms=slot_clarification_stage_ms,
            business_resolution=business_resolution,
            executive_reasoning=executive_reasoning,
            guided_fallback=guided_fallback,
        )
