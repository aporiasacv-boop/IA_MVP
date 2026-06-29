"""Infrastructure Adapter del chat híbrido.

``HybridChatRouter`` adapta artefactos internos del Business Pipeline al contrato
público ``HybridChatResult``, coordina la integración legacy y centraliza la
observabilidad de performance del adaptador.

No contiene lógica de dominio de negocio: clasificación, resolución, executive
reasoning y guided fallback se orquestan en ``BusinessPipelineCapability``.

Deuda técnica residual (Sprint 21): la coordinación de persistencia conversacional
post-adaptación (``save_context``, ``persist_*``, ``finalize_memory_resolution``)
permanece aquí porque el pipeline no debe duplicar esos efectos secundarios sin
un contrato explícito de cierre de turno.
"""

import time
from collections.abc import Callable
from dataclasses import dataclass

from app.conversation_memory.context_resolver import ContextResolution
from app.conversation_memory.schemas import ConversationContext
from app.capabilities.business_pipeline_state import BusinessPipelineState
from app.capabilities.conversation_context_capability import ConversationContextCapability
from app.query_engine.query_types import BusinessQueryType
from app.observability.performance_metrics import elapsed_ms
from app.observability.performance_tracker import PerformanceTracker
from app.schemas.chat import ChatResponse
from app.schemas.hybrid_chat import HybridChatResult
from app.slot_clarification.schemas import SlotClarificationResult

LegacyChatHandler = Callable[[str], ChatResponse]


@dataclass(frozen=True)
class HybridRouteOutcome:
    """Resultado de adaptación sin enriquecimiento conversacional."""

    result: HybridChatResult
    collector: object | None = None


class HybridChatRouter:
    """Infrastructure Adapter: contrato público, legacy y observabilidad.

    Responsabilidades permitidas:
    - Adaptación de resultados internos a ``HybridChatResult``.
    - Compatibilidad con el stack legacy vía ``LegacyChatHandler``.
    - Observabilidad de performance del adaptador.
    """

    HANDLED_BY_BUSINESS = "business_pipeline"
    HANDLED_BY_LEGACY = "legacy_chat"
    HANDLED_BY_SLOT_CLARIFICATION = "slot_clarification"
    HANDLED_BY_CONVERSATION_MEMORY = "conversation_memory"

    def __init__(
        self,
        legacy_chat_handler: LegacyChatHandler,
        conversation_context: ConversationContextCapability | None = None,
        performance_tracker: PerformanceTracker | None = None,
    ) -> None:
        self._legacy_chat_handler = legacy_chat_handler
        self._conversation_context = (
            conversation_context or ConversationContextCapability()
        )
        self._performance_tracker = performance_tracker

    def route(
        self,
        message: str,
        *,
        pipeline_state: BusinessPipelineState,
    ) -> HybridRouteOutcome:
        """Adapta el estado del pipeline al contrato público de respuesta."""
        session_id = pipeline_state.session_id
        context = pipeline_state.context
        memory_resolution = pipeline_state.memory_resolution

        collector = (
            self._performance_tracker.start_request(message)
            if self._performance_tracker is not None
            else None
        )

        try:
            if (
                collector
                and self._performance_tracker is not None
                and pipeline_state.conversation_memory_stage_ms is not None
            ):
                self._performance_tracker.record_stage(
                    collector,
                    "conversation_memory",
                    pipeline_state.conversation_memory_stage_ms,
                )

            if memory_resolution is not None:
                result = self._adapt_conversation_memory(
                    memory_resolution,
                    session_id=session_id,
                    context=context,
                    collector=collector,
                    pipeline_state=pipeline_state,
                )
            else:
                result = self._adapt_without_memory(
                    message,
                    session_id=session_id,
                    context=context,
                    collector=collector,
                    pipeline_state=pipeline_state,
                )

            return HybridRouteOutcome(result=result, collector=collector)
        except Exception:
            if collector and self._performance_tracker is not None:
                from app.observability.performance_metrics import set_active_collector

                set_active_collector(None)
            raise

    def finalize_observability(
        self,
        result: HybridChatResult,
        *,
        collector: object | None,
    ) -> None:
        """Cierra y persiste métricas de performance del adaptador."""
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

    def _adapt_without_memory(
        self,
        message: str,
        *,
        session_id: str,
        context: ConversationContext,
        collector,
        pipeline_state: BusinessPipelineState,
    ) -> HybridChatResult:
        understanding = pipeline_state.business_understanding
        if understanding is None:
            raise ValueError("business_understanding es obligatorio cuando no hay resolución de memoria")

        intent = understanding.result.intent
        query = understanding.result.query

        if collector and self._performance_tracker is not None:
            self._performance_tracker.record_stage(
                collector,
                "intent",
                understanding.intent_stage_ms,
            )
            self._performance_tracker.record_stage(
                collector,
                "planner",
                understanding.planner_stage_ms,
            )

        if query.query_type != BusinessQueryType.UNSUPPORTED:
            if (
                collector
                and self._performance_tracker is not None
                and pipeline_state.slot_clarification_stage_ms is not None
            ):
                self._performance_tracker.record_stage(
                    collector,
                    "slot_clarification",
                    pipeline_state.slot_clarification_stage_ms,
                )

            clarification = pipeline_state.slot_clarification
            if clarification is not None:
                self._conversation_context.persist_slot_clarification(
                    context, intent, query, clarification
                )
                self._conversation_context.save_context(session_id, context)
                return self._adapt_slot_clarification(
                    clarification,
                    session_id=session_id,
                    confidence=intent.confidence,
                )

            resolution = pipeline_state.business_resolution
            if resolution is None:
                raise ValueError("business_resolution es obligatorio para consultas soportadas")

            if collector and self._performance_tracker is not None:
                self._performance_tracker.record_stage(
                    collector,
                    "executor",
                    resolution.executor_stage_ms,
                )
                self._performance_tracker.record_stage(
                    collector,
                    "response",
                    resolution.response_stage_ms,
                )

            result = self._adapt_business_pipeline(
                resolution.result.response,
                query_type=query.query_type.value,
                confidence=intent.confidence,
            )
            self._conversation_context.persist_successful_query(context, intent, query)
            context.pending_clarification = None
            self._conversation_context.save_context(session_id, context)
            return result

        executive_reasoning = pipeline_state.executive_reasoning
        if executive_reasoning is not None:
            if collector and self._performance_tracker is not None:
                self._performance_tracker.record_stage(
                    collector,
                    "executive_reasoning",
                    executive_reasoning.stage_ms,
                )
            self._conversation_context.save_context(session_id, context)
            return executive_reasoning.result

        guided_fallback = pipeline_state.guided_fallback
        if guided_fallback is not None:
            if collector and self._performance_tracker is not None:
                self._performance_tracker.record_stage(
                    collector,
                    "guided_fallback",
                    guided_fallback.stage_ms,
                )
            self._conversation_context.save_context(session_id, context)
            return guided_fallback.result

        result = self._adapt_legacy_chat(message, collector=collector)
        self._conversation_context.save_context(session_id, context)
        return result

    def _adapt_conversation_memory(
        self,
        resolution: ContextResolution,
        *,
        session_id: str,
        context: ConversationContext,
        collector,
        pipeline_state: BusinessPipelineState,
    ) -> HybridChatResult:
        query = resolution.query
        business_resolution = pipeline_state.business_resolution
        if business_resolution is None:
            raise ValueError("business_resolution es obligatorio cuando hay resolución de memoria")

        if collector and self._performance_tracker is not None:
            self._performance_tracker.record_stage(
                collector,
                "executor",
                business_resolution.executor_stage_ms,
            )
            self._performance_tracker.record_stage(
                collector,
                "response",
                business_resolution.response_stage_ms,
            )

        response = business_resolution.result.response

        memory_metadata = self._conversation_context.finalize_memory_resolution(
            session_id,
            context,
            query,
            resolution,
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

    def _adapt_business_pipeline(
        self,
        response,
        *,
        query_type: str,
        confidence: float,
    ) -> HybridChatResult:
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

    def _adapt_slot_clarification(
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

    def _adapt_legacy_chat(self, message: str, *, collector) -> HybridChatResult:
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
