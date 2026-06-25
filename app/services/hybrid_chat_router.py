import time
import uuid
from collections.abc import Callable

from app.conversation_memory.context_resolver import ContextResolution, ContextResolver, is_new_question
from app.conversation_memory.schemas import ConversationContext
from app.conversation_memory.service import ConversationMemoryService
from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_types import BusinessQueryType
from app.query_executor.business_query_executor import BusinessQueryExecutor
from app.query_engine.query_planner import BusinessQueryPlanner
from app.observability.performance_metrics import elapsed_ms
from app.observability.performance_tracker import PerformanceTracker
from app.response_engine.deterministic_response_engine import DeterministicResponseEngine
from app.schemas.chat import ChatResponse
from app.schemas.hybrid_chat import HybridChatResult
from app.schemas.semantic_intent import BusinessSemanticIntent
from app.services.semantic_intent_builder import SemanticIntentBuilder
from app.capability_discovery.detector import is_capability_discovery
from app.enterprise_knowledge_service.integration.consumers import knowledge_for_capability_discovery
from app.capability_discovery.engine import CapabilityDiscoveryEngine
from app.capability_discovery.schemas import CapabilityDiscoveryResult
from app.guided_fallback.engine import GuidedFallbackEngine
from app.guided_fallback.schemas import GuidedFallbackResult
from app.suggested_questions.engine import SuggestedQuestionsEngine
from app.slot_clarification.engine import SlotClarificationEngine
from app.slot_clarification.schemas import SlotClarificationResult
from app.coverage_recovery.metrics import CoverageRecoveryMetricsService
from app.core.settings import settings

LegacyChatHandler = Callable[[str], ChatResponse]
ExecutiveReasoningHandler = Callable[[str], "HybridChatResult"]


class HybridChatRouter:
    HANDLED_BY_BUSINESS = "business_pipeline"
    HANDLED_BY_LEGACY = "legacy_chat"
    HANDLED_BY_SLOT_CLARIFICATION = "slot_clarification"
    HANDLED_BY_CONVERSATION_MEMORY = "conversation_memory"
    HANDLED_BY_GUIDED_FALLBACK = "guided_fallback"
    HANDLED_BY_CAPABILITY_DISCOVERY = "capability_discovery"
    HANDLED_BY_EXECUTIVE_REASONING = "executive_reasoning"

    def __init__(
        self,
        intent_builder: SemanticIntentBuilder,
        query_planner: BusinessQueryPlanner,
        query_executor: BusinessQueryExecutor,
        response_engine: DeterministicResponseEngine,
        legacy_chat_handler: LegacyChatHandler,
        slot_clarification_engine: SlotClarificationEngine | None = None,
        conversation_memory_service: ConversationMemoryService | None = None,
        context_resolver: ContextResolver | None = None,
        guided_fallback_engine: GuidedFallbackEngine | None = None,
        capability_discovery_engine: CapabilityDiscoveryEngine | None = None,
        suggested_questions_engine: SuggestedQuestionsEngine | None = None,
        performance_tracker: PerformanceTracker | None = None,
        executive_reasoning_handler: ExecutiveReasoningHandler | None = None,
    ) -> None:
        self._intent_builder = intent_builder
        self._query_planner = query_planner
        self._query_executor = query_executor
        self._response_engine = response_engine
        self._legacy_chat_handler = legacy_chat_handler
        self._slot_clarification_engine = (
            slot_clarification_engine or SlotClarificationEngine()
        )
        self._conversation_memory_service = (
            conversation_memory_service or ConversationMemoryService()
        )
        self._context_resolver = context_resolver or ContextResolver()
        self._guided_fallback_engine = (
            guided_fallback_engine or GuidedFallbackEngine()
        )
        self._capability_discovery_engine = (
            capability_discovery_engine or CapabilityDiscoveryEngine()
        )
        self._suggested_questions_engine = (
            suggested_questions_engine or SuggestedQuestionsEngine()
        )
        self._performance_tracker = performance_tracker
        self._executive_reasoning_handler = executive_reasoning_handler

    def route(self, message: str, session_id: str | None = None) -> HybridChatResult:
        session_id = session_id or uuid.uuid4().hex
        context = self._conversation_memory_service.get_or_create(session_id)

        collector = (
            self._performance_tracker.start_request(message)
            if self._performance_tracker is not None
            else None
        )

        try:
            if context.pending_clarification and is_new_question(message):
                context.pending_clarification = None
                self._conversation_memory_service.save_context(session_id, context)

            memory_started = time.perf_counter()
            memory_resolution = self._context_resolver.resolve(message, context)
            if collector and self._performance_tracker is not None:
                self._performance_tracker.record_stage(
                    collector,
                    "conversation_memory",
                    elapsed_ms(memory_started),
                )

            if memory_resolution is not None:
                self._conversation_memory_service.record_hit(
                    clarification=memory_resolution.resolution_type == "clarification",
                )
                result = self._handle_conversation_memory(
                    memory_resolution,
                    session_id=session_id,
                    context=context,
                    collector=collector,
                )
            else:
                if context.turn_count > 0 or context.pending_clarification:
                    self._conversation_memory_service.record_miss()
                result = self._route_without_memory(
                    message,
                    session_id=session_id,
                    context=context,
                    collector=collector,
                )

            result = self._attach_suggestions(result, context=context)
            CoverageRecoveryMetricsService.record_outcome(message, result)

            if collector and self._performance_tracker is not None:
                metrics = self._performance_tracker.finish_request(
                    collector,
                    handled_by=result.handled_by,
                    success=result.success,
                    query_type=(
                        result.metadata.get("query_type")
                        or result.metadata.get("fallback_type")
                        or result.metadata.get("pending_query_type")
                    ),
                    suggested_questions_count=(
                        len(result.suggestions.questions)
                        if result.suggestions is not None
                        else None
                    ),
                )
                self._performance_tracker.persist(metrics)

            return result
        except Exception:
            if collector and self._performance_tracker is not None:
                from app.observability.performance_metrics import set_active_collector

                set_active_collector(None)
            raise

    def _route_without_memory(
        self,
        message: str,
        *,
        session_id: str,
        context: ConversationContext,
        collector,
    ) -> HybridChatResult:
        intent_started = time.perf_counter()
        intent = self._intent_builder.build(message)
        if collector and self._performance_tracker is not None:
            self._performance_tracker.record_stage(
                collector,
                "intent",
                elapsed_ms(intent_started),
            )

        planner_started = time.perf_counter()
        query = self._query_planner.plan(intent)
        if collector and self._performance_tracker is not None:
            self._performance_tracker.record_stage(
                collector,
                "planner",
                elapsed_ms(planner_started),
            )

        if query.query_type == BusinessQueryType.SYSTEM_CAPABILITIES:
            payload = knowledge_for_capability_discovery()
            answer, capabilities, examples = payload.answer, payload.capabilities, payload.examples
            result = HybridChatResult(
                handled_by="business_knowledge",
                success=True,
                answer=answer,
                metadata={
                    "handled_by": "business_knowledge",
                    "query_type": "SYSTEM_CAPABILITIES",
                    "confidence": 1.0,
                    "knowledge_source": "knowledge_pack/executive/capacidades-asistente.md",
                    "knowledge_match_type": "system_capabilities_redirect",
                    "capabilities_count": len(capabilities),
                    "example_questions_count": len(examples),
                },
            )
            self._conversation_memory_service.save_context(session_id, context)
            return self._attach_suggestions(result, context=context)

        if query.query_type != BusinessQueryType.UNSUPPORTED:
            clarification_started = time.perf_counter()
            clarification = self._slot_clarification_engine.resolve(intent, query)
            if collector and self._performance_tracker is not None:
                self._performance_tracker.record_stage(
                    collector,
                    "slot_clarification",
                    elapsed_ms(clarification_started),
                )

            if clarification is not None:
                self._persist_slot_clarification(context, intent, query, clarification)
                self._conversation_memory_service.save_context(session_id, context)
                return self._handle_slot_clarification(
                    clarification,
                    session_id=session_id,
                    confidence=intent.confidence,
                )

            result = self._handle_business_pipeline(
                query,
                query_type=query.query_type.value,
                confidence=intent.confidence,
                collector=collector,
            )
            self._persist_successful_query(context, intent, query)
            context.pending_clarification = None
            self._conversation_memory_service.save_context(session_id, context)
            return result

        if (
            settings.EXECUTIVE_REASONING_ENABLED
            and self._executive_reasoning_handler is not None
            and self._is_executive_reasoning_candidate(message)
        ):
            executive_started = time.perf_counter()
            result = self._handle_executive_reasoning(message, collector=collector)
            if collector and self._performance_tracker is not None:
                self._performance_tracker.record_stage(
                    collector,
                    "executive_reasoning",
                    elapsed_ms(executive_started),
                )
            self._conversation_memory_service.save_context(session_id, context)
            return result

        fallback_started = time.perf_counter()
        fallback = self._guided_fallback_engine.resolve(
            message,
            intent,
            query,
            context,
        )
        if collector and self._performance_tracker is not None:
            self._performance_tracker.record_stage(
                collector,
                "guided_fallback",
                elapsed_ms(fallback_started),
            )

        if fallback is not None:
            self._conversation_memory_service.save_context(session_id, context)
            return self._handle_guided_fallback(fallback, session_id=session_id)

        result = self._handle_legacy_chat(message, collector=collector)
        self._conversation_memory_service.save_context(session_id, context)
        return result

    def _handle_conversation_memory(
        self,
        resolution: ContextResolution,
        *,
        session_id: str,
        context: ConversationContext,
        collector,
    ) -> HybridChatResult:
        query = resolution.query
        executor_started = time.perf_counter()
        query_result = self._query_executor.execute(query)
        if collector and self._performance_tracker is not None:
            self._performance_tracker.record_stage(
                collector,
                "executor",
                elapsed_ms(executor_started),
            )

        response_started = time.perf_counter()
        response = self._response_engine.generate(query_result)
        if collector and self._performance_tracker is not None:
            self._performance_tracker.record_stage(
                collector,
                "response",
                elapsed_ms(response_started),
            )

        context.last_query_type = query.query_type.value
        context.last_filters = dict(query.filters)
        context.pending_clarification = None
        if resolution.resolution_type == "follow_up":
            pass
        self._conversation_memory_service.save_context(session_id, context)

        memory_metadata = self._memory_metadata(
            context_hit=True,
            resolution_type=resolution.resolution_type,
            inherited_from=resolution.inherited_from,
            clarification_resolved=resolution.resolution_type == "clarification",
        )

        return HybridChatResult(
            handled_by=self.HANDLED_BY_CONVERSATION_MEMORY,
            success=response.success,
            answer=response.answer,
            metadata={
                "handled_by": self.HANDLED_BY_CONVERSATION_MEMORY,
                "query_type": query.query_type.value,
                "session_id": session_id,
                **memory_metadata,
            },
        )

    def _handle_business_pipeline(
        self,
        query,
        *,
        query_type: str,
        confidence: float,
        collector,
    ) -> HybridChatResult:
        executor_started = time.perf_counter()
        query_result = self._query_executor.execute(query)
        if collector and self._performance_tracker is not None:
            self._performance_tracker.record_stage(
                collector,
                "executor",
                elapsed_ms(executor_started),
            )

        response_started = time.perf_counter()
        response = self._response_engine.generate(query_result)
        if collector and self._performance_tracker is not None:
            self._performance_tracker.record_stage(
                collector,
                "response",
                elapsed_ms(response_started),
            )

        return HybridChatResult(
            handled_by=self.HANDLED_BY_BUSINESS,
            success=response.success,
            answer=response.answer,
            metadata={
                "handled_by": self.HANDLED_BY_BUSINESS,
                "query_type": query_type,
                "confidence": confidence,
            },
        )

    def _handle_slot_clarification(
        self,
        clarification: SlotClarificationResult,
        *,
        session_id: str,
        confidence: float,
    ) -> HybridChatResult:
        return HybridChatResult(
            handled_by=self.HANDLED_BY_SLOT_CLARIFICATION,
            success=clarification.success,
            answer=clarification.answer,
            metadata={
                "handled_by": self.HANDLED_BY_SLOT_CLARIFICATION,
                "query_type": clarification.pending_query_type,
                "pending_query_type": clarification.pending_query_type,
                "missing_slots": clarification.missing_slots,
                "session_token": clarification.session_token,
                "session_id": session_id,
                "confidence": confidence,
                **clarification.metadata,
            },
        )

    def _handle_capability_discovery(
        self,
        discovery: CapabilityDiscoveryResult,
        *,
        session_id: str,
    ) -> HybridChatResult:
        return HybridChatResult(
            handled_by=self.HANDLED_BY_CAPABILITY_DISCOVERY,
            success=discovery.success,
            answer=discovery.answer,
            metadata={
                "handled_by": self.HANDLED_BY_CAPABILITY_DISCOVERY,
                "query_type": "capability_discovery",
                "capabilities": discovery.capabilities,
                "capabilities_count": discovery.metadata.get(
                    "capabilities_count",
                    len(discovery.capabilities),
                ),
                "example_questions": discovery.example_questions,
                "example_questions_count": discovery.metadata.get(
                    "example_questions_count",
                    len(discovery.example_questions),
                ),
                "discovery_success": discovery.metadata.get("discovery_success", True),
                "session_id": session_id,
                **discovery.metadata,
            },
        )

    def _handle_guided_fallback(
        self,
        fallback: GuidedFallbackResult,
        *,
        session_id: str,
    ) -> HybridChatResult:
        return HybridChatResult(
            handled_by=self.HANDLED_BY_GUIDED_FALLBACK,
            success=fallback.success,
            answer=fallback.answer,
            metadata={
                "handled_by": self.HANDLED_BY_GUIDED_FALLBACK,
                "fallback_type": fallback.fallback_type,
                "suggested_questions": fallback.suggested_questions,
                "suggested_questions_count": len(fallback.suggested_questions),
                "fallback_success": fallback.metadata.get("fallback_success", True),
                "session_id": session_id,
                **fallback.metadata,
            },
        )

    def _handle_executive_reasoning(self, message: str, *, collector) -> HybridChatResult:
        assert self._executive_reasoning_handler is not None
        return self._executive_reasoning_handler(message)

    @staticmethod
    def _is_executive_reasoning_candidate(message: str) -> bool:
        from app.ai_orchestration.service import is_executive_reasoning_candidate

        return is_executive_reasoning_candidate(message)

    def _handle_legacy_chat(self, message: str, *, collector) -> HybridChatResult:
        legacy_started = time.perf_counter()
        legacy_response = self._legacy_chat_handler(message)
        if collector and self._performance_tracker is not None:
            self._performance_tracker.record_stage(
                collector,
                "legacy_chat",
                elapsed_ms(legacy_started),
            )
            if legacy_response.timings.llm_ms > 0:
                self._performance_tracker.record_stage(
                    collector,
                    "ollama",
                    legacy_response.timings.llm_ms,
                )

        return HybridChatResult(
            handled_by=self.HANDLED_BY_LEGACY,
            success=bool(legacy_response.answer),
            answer=legacy_response.answer,
            metadata={
                "handled_by": self.HANDLED_BY_LEGACY,
                "intent": legacy_response.intent,
                "confidence": legacy_response.intent_confidence,
                "response_mode": legacy_response.response_mode.value,
            },
        )

    def _attach_suggestions(
        self,
        result: HybridChatResult,
        *,
        context: ConversationContext,
    ) -> HybridChatResult:
        if result.handled_by == self.HANDLED_BY_CAPABILITY_DISCOVERY:
            metadata = {
                **result.metadata,
                "suggested_questions": [],
                "suggested_questions_count": 0,
                "suggested_questions_source": "none",
                "suggested_questions_generated": False,
                "suggested_questions_clicked": 0,
                **CoverageRecoveryMetricsService.snapshot(),
            }
            return HybridChatResult(
                handled_by=result.handled_by,
                success=result.success,
                answer=result.answer,
                suggestions=None,
                metadata=metadata,
            )

        query_type = (
            result.metadata.get("query_type")
            or result.metadata.get("pending_query_type")
            or result.metadata.get("fallback_type")
        )
        confidence = result.metadata.get("confidence")
        if not isinstance(confidence, (int, float)):
            confidence = None

        suggestions = self._suggested_questions_engine.generate(
            current_query_type=query_type,
            current_operation=context.last_operation,
            current_entity=context.last_target_entity,
            conversation_context=context,
            handled_by=result.handled_by,
            confidence=confidence,
        )

        metadata = {
            **result.metadata,
            "suggested_questions": suggestions.questions,
            "suggested_questions_count": len(suggestions.questions),
            "suggested_questions_source": suggestions.source,
            "suggested_questions_generated": len(suggestions.questions) > 0,
            "suggested_questions_clicked": 0,
            **CoverageRecoveryMetricsService.snapshot(),
        }

        return HybridChatResult(
            handled_by=result.handled_by,
            success=result.success,
            answer=result.answer,
            suggestions=suggestions,
            metadata=metadata,
        )

    @staticmethod
    def _persist_slot_clarification(
        context: ConversationContext,
        intent: BusinessSemanticIntent,
        query: BusinessQuery,
        clarification: SlotClarificationResult,
    ) -> None:
        context.last_query_type = clarification.pending_query_type
        context.last_operation = (
            intent.operation.value if intent.operation is not None else None
        )
        context.last_target_entity = (
            intent.target_entity.value if intent.target_entity is not None else None
        )
        context.last_filters = dict(query.filters)
        context.pending_clarification = {
            "pending_query_type": clarification.pending_query_type,
            "missing_slots": clarification.missing_slots,
            "session_token": clarification.session_token,
            "pending_filters": clarification.metadata.get("pending_filters", {}),
        }

    @staticmethod
    def _persist_successful_query(
        context: ConversationContext,
        intent: BusinessSemanticIntent,
        query: BusinessQuery,
    ) -> None:
        context.last_query_type = query.query_type.value
        context.last_operation = (
            intent.operation.value if intent.operation is not None else None
        )
        context.last_target_entity = (
            intent.target_entity.value if intent.target_entity is not None else None
        )
        context.last_filters = dict(query.filters)

    @staticmethod
    def _memory_metadata(
        *,
        context_hit: bool,
        resolution_type: str,
        inherited_from: str,
        clarification_resolved: bool,
    ) -> dict:
        snapshot = ConversationMemoryService.snapshot_metrics()
        return {
            "context_hit": context_hit,
            "resolution_type": resolution_type,
            "inherited_from": inherited_from,
            "clarification_resolved": clarification_resolved,
            "context_hits": snapshot["context_hits"],
            "context_misses": snapshot["context_misses"],
            "clarification_resolutions": snapshot["clarification_resolutions"],
        }
