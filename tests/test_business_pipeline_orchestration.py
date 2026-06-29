from unittest.mock import MagicMock

import pytest

from app.capabilities.business_pipeline_capability import BusinessPipelineCapability
from app.capabilities.business_resolution_capability import (
    BusinessResolutionCapability,
    BusinessResolutionResult,
    BusinessResolutionStage,
)
from app.capabilities.business_understanding_capability import (
    BusinessUnderstandingCapability,
    BusinessUnderstandingResult,
    BusinessUnderstandingStage,
)
from app.capabilities.conversation_context_capability import ConversationContextCapability
from app.conversation_memory.context_resolver import ContextResolution
from app.conversation_memory.schemas import ConversationContext
from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_types import BusinessQueryType
from app.response_engine.response_result import BusinessResponse
from app.schemas.hybrid_chat import HybridChatResult
from app.services.hybrid_chat_router import HybridRouteOutcome


def _passthrough_enrichment() -> MagicMock:
    enrichment = MagicMock()
    enrichment.enrich.side_effect = lambda result, context=None: result
    return enrichment


def _mock_institutional() -> MagicMock:
    return MagicMock()


def _mock_executive() -> MagicMock:
    return MagicMock()


def _mock_guided_fallback() -> MagicMock:
    return MagicMock()


def test_prepare_pipeline_state_resolves_session(conversation_context: ConversationContextCapability) -> None:
    preparer = BusinessPipelineCapability(
        MagicMock(),
        _passthrough_enrichment(),
        conversation_context,
        BusinessUnderstandingCapability(),
        BusinessResolutionCapability(MagicMock(), MagicMock()),
        _mock_institutional(),
        _mock_executive(),
        _mock_guided_fallback(),
    )

    state = preparer._prepare_pipeline_state("hola", None)

    assert state.session_id
    assert state.context.session_id == state.session_id
    assert state.memory_resolution is None
    assert state.conversation_memory_stage_ms is not None
    assert state.business_understanding is not None


def test_prepare_pipeline_state_skips_understanding_on_memory_hit() -> None:
    conversation_context = MagicMock()
    context = ConversationContext(session_id="sess-hit")
    resolution = ContextResolution(
        query=BusinessQuery(query_type=BusinessQueryType.COUNT_CLIENTES),
        resolution_type="follow_up",
        inherited_from="COUNT_PROVEEDORES",
    )
    conversation_context.prepare_session.return_value = ("sess-hit", context)
    conversation_context.resolve.return_value = resolution
    business_understanding = MagicMock()
    business_resolution = MagicMock()
    business_resolution.resolve.return_value = BusinessResolutionStage(
        result=BusinessResolutionResult(
            query_result=MagicMock(),
            response=BusinessResponse(
                success=True,
                answer="50 clientes",
                query_type="COUNT_CLIENTES",
            ),
        ),
        executor_stage_ms=1.0,
        response_stage_ms=2.0,
    )

    preparer = BusinessPipelineCapability(
        MagicMock(),
        _passthrough_enrichment(),
        conversation_context,
        business_understanding,
        business_resolution,
        _mock_institutional(),
        _mock_executive(),
        _mock_guided_fallback(),
    )
    state = preparer._prepare_pipeline_state("¿Y clientes?", "sess-hit")

    business_understanding.understand.assert_not_called()
    assert state.business_understanding is None
    assert state.memory_resolution is resolution
    business_resolution.resolve.assert_called_once_with(resolution.query)
    assert state.business_resolution is not None


def test_execute_orchestrates_context_before_router() -> None:
    router = MagicMock()
    conversation_context = MagicMock()
    conversation_context.prepare_session.return_value = ("sess-1", ConversationContext(session_id="sess-1"))
    conversation_context.resolve.return_value = None
    business_understanding = MagicMock()
    business_understanding.understand.return_value = BusinessUnderstandingStage(
        result=BusinessUnderstandingResult(
            intent=MagicMock(confidence=0.9),
            query=BusinessQuery(query_type=BusinessQueryType.COUNT_CLIENTES),
        ),
        intent_stage_ms=1.0,
        planner_stage_ms=2.0,
    )
    business_resolution = MagicMock()
    business_resolution.resolve.return_value = BusinessResolutionStage(
        result=BusinessResolutionResult(
            query_result=MagicMock(),
            response=BusinessResponse(
                success=True,
                answer="ok",
                query_type="COUNT_CLIENTES",
            ),
        ),
        executor_stage_ms=1.0,
        response_stage_ms=1.0,
    )

    expected = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="ok",
        metadata={},
    )
    router.route.return_value = HybridRouteOutcome(result=expected)

    capability = BusinessPipelineCapability(
        router,
        _passthrough_enrichment(),
        conversation_context,
        business_understanding,
        business_resolution,
        _mock_institutional(),
        _mock_executive(),
        _mock_guided_fallback(),
    )
    result = capability.execute("cuantos clientes", session_id="sess-1")

    conversation_context.prepare_session.assert_called_once_with("cuantos clientes", "sess-1")
    conversation_context.resolve.assert_called_once()
    conversation_context.record_memory_miss_if_applicable.assert_called_once()
    business_understanding.understand.assert_called_once_with("cuantos clientes")
    business_resolution.resolve.assert_called_once()
    router.route.assert_called_once()
    call_kwargs = router.route.call_args.kwargs
    assert call_kwargs["pipeline_state"].session_id == "sess-1"
    assert call_kwargs["pipeline_state"].business_understanding is not None
    assert call_kwargs["pipeline_state"].business_resolution is not None
    assert result is expected


def test_execute_records_memory_hit_when_resolved() -> None:
    router = MagicMock()
    conversation_context = MagicMock()
    business_understanding = MagicMock()
    business_resolution = MagicMock()
    context = ConversationContext(session_id="sess-2")
    resolution = ContextResolution(
        query=BusinessQuery(query_type=BusinessQueryType.COUNT_CLIENTES),
        resolution_type="follow_up",
        inherited_from="COUNT_PROVEEDORES",
    )
    conversation_context.prepare_session.return_value = ("sess-2", context)
    conversation_context.resolve.return_value = resolution
    router.route.return_value = HybridRouteOutcome(
        result=HybridChatResult(
            handled_by="conversation_memory",
            success=True,
            answer="50 clientes",
            metadata={},
        ),
    )

    capability = BusinessPipelineCapability(
        router,
        _passthrough_enrichment(),
        conversation_context,
        business_understanding,
        business_resolution,
        _mock_institutional(),
        _mock_executive(),
        _mock_guided_fallback(),
    )
    capability.execute("¿Y clientes?", session_id="sess-2")

    conversation_context.record_memory_hit.assert_called_once_with(resolution)
    conversation_context.record_memory_miss_if_applicable.assert_not_called()
    business_understanding.understand.assert_not_called()
    business_resolution.resolve.assert_called_once_with(resolution.query)
    assert router.route.call_args.kwargs["pipeline_state"].memory_resolution is resolution


def test_execute_orchestrates_enrichment_after_router() -> None:
    router = MagicMock()
    conversation_context = MagicMock()
    context = ConversationContext(session_id="sess-enrich")
    conversation_context.prepare_session.return_value = ("sess-enrich", context)
    conversation_context.resolve.return_value = None
    business_understanding = MagicMock()
    business_understanding.understand.return_value = MagicMock()
    business_resolution = MagicMock()
    business_resolution.resolve.return_value = MagicMock()

    raw = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="sin enriquecer",
        metadata={},
    )
    enriched = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="enriquecido",
        metadata={"suggestions_attached": True},
    )
    collector = object()
    router.route.return_value = HybridRouteOutcome(result=raw, collector=collector)

    enrichment = MagicMock()
    enrichment.enrich.return_value = enriched

    capability = BusinessPipelineCapability(
        router,
        enrichment,
        conversation_context,
        business_understanding,
        business_resolution,
        _mock_institutional(),
        _mock_executive(),
        _mock_guided_fallback(),
    )
    result = capability.execute("cuantos clientes", session_id="sess-enrich")

    enrichment.enrich.assert_called_once_with(raw, context=context)
    router.finalize_observability.assert_called_once_with(
        enriched,
        collector=collector,
    )
    assert result is enriched


def test_execute_orchestrates_institutional_before_router_for_system_capabilities() -> None:
    router = MagicMock()
    conversation_context = MagicMock()
    context = ConversationContext(session_id="sess-cap")
    conversation_context.prepare_session.return_value = ("sess-cap", context)
    conversation_context.resolve.return_value = None
    business_understanding = MagicMock()
    business_understanding.understand.return_value = BusinessUnderstandingStage(
        result=BusinessUnderstandingResult(
            intent=MagicMock(confidence=1.0),
            query=BusinessQuery(query_type=BusinessQueryType.SYSTEM_CAPABILITIES),
        ),
        intent_stage_ms=1.0,
        planner_stage_ms=1.0,
    )
    institutional = MagicMock()
    institutional_result = HybridChatResult(
        handled_by="business_knowledge",
        success=True,
        answer="Puedo consultar clientes y proveedores.",
        metadata={"query_type": "SYSTEM_CAPABILITIES"},
    )
    institutional.resolve_system_capabilities.return_value = institutional_result

    capability = BusinessPipelineCapability(
        router,
        _passthrough_enrichment(),
        conversation_context,
        business_understanding,
        MagicMock(),
        institutional,
        _mock_executive(),
        _mock_guided_fallback(),
    )
    result = capability.execute("¿Qué puedo preguntarte?", session_id="sess-cap")

    institutional.resolve_system_capabilities.assert_called_once_with("¿Qué puedo preguntarte?")
    conversation_context.save_context.assert_called_once_with("sess-cap", context)
    router.route.assert_not_called()
    assert result is institutional_result


def test_prepare_pipeline_state_runs_executive_reasoning_for_unsupported_candidates() -> None:
    conversation_context = MagicMock()
    context = ConversationContext(session_id="sess-exec")
    conversation_context.prepare_session.return_value = ("sess-exec", context)
    conversation_context.resolve.return_value = None
    business_understanding = MagicMock()
    business_understanding.understand.return_value = BusinessUnderstandingStage(
        result=BusinessUnderstandingResult(
            intent=MagicMock(confidence=0.8),
            query=BusinessQuery(query_type=BusinessQueryType.UNSUPPORTED),
        ),
        intent_stage_ms=1.0,
        planner_stage_ms=1.0,
    )
    executive = MagicMock()
    executive_stage = MagicMock()
    executive_stage.result = HybridChatResult(
        handled_by="executive_reasoning",
        success=True,
        answer="Análisis ejecutivo.",
        metadata={"handled_by": "executive_reasoning"},
    )
    executive_stage.stage_ms = 42.0
    executive.try_reason.return_value = executive_stage

    preparer = BusinessPipelineCapability(
        MagicMock(),
        _passthrough_enrichment(),
        conversation_context,
        business_understanding,
        MagicMock(),
        _mock_institutional(),
        executive,
        _mock_guided_fallback(),
    )
    state = preparer._prepare_pipeline_state(
        "Evaluar riesgos del cliente principal",
        "sess-exec",
    )

    executive.try_reason.assert_called_once_with("Evaluar riesgos del cliente principal")
    assert state.executive_reasoning is executive_stage
    assert state.business_resolution is None


def test_prepare_pipeline_state_runs_guided_fallback_when_executive_skips() -> None:
    conversation_context = MagicMock()
    context = ConversationContext(session_id="sess-fallback")
    conversation_context.prepare_session.return_value = ("sess-fallback", context)
    conversation_context.resolve.return_value = None
    business_understanding = MagicMock()
    business_understanding.understand.return_value = BusinessUnderstandingStage(
        result=BusinessUnderstandingResult(
            intent=MagicMock(confidence=0.4),
            query=BusinessQuery(query_type=BusinessQueryType.UNSUPPORTED),
        ),
        intent_stage_ms=1.0,
        planner_stage_ms=1.0,
    )
    executive = MagicMock()
    executive.try_reason.return_value = None
    guided = MagicMock()
    fallback_stage = MagicMock()
    fallback_stage.result = HybridChatResult(
        handled_by="guided_fallback",
        success=True,
        answer="Asistencia guiada.",
        metadata={"handled_by": "guided_fallback"},
    )
    guided.try_fallback.return_value = fallback_stage

    preparer = BusinessPipelineCapability(
        MagicMock(),
        _passthrough_enrichment(),
        conversation_context,
        business_understanding,
        MagicMock(),
        _mock_institutional(),
        executive,
        guided,
    )
    state = preparer._prepare_pipeline_state("¿Cómo va el negocio?", "sess-fallback")

    executive.try_reason.assert_called_once_with("¿Cómo va el negocio?")
    guided.try_fallback.assert_called_once()
    assert state.guided_fallback is fallback_stage
