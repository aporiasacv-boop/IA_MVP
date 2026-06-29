from unittest.mock import MagicMock

from app.capabilities.business_pipeline_capability import BusinessPipelineCapability
from app.conversation_memory.schemas import ConversationContext
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


def test_execute_delegates_to_hybrid_router_with_prepared_state():
    router = MagicMock()
    conversation_context = MagicMock()
    conversation_context.prepare_session.return_value = ("sess-42", ConversationContext(session_id="sess-42"))
    conversation_context.resolve.return_value = None
    expected = HybridChatResult(
        handled_by="business_pipeline",
        success=True,
        answer="Actualmente existen 50 clientes registrados.",
        metadata={"query_type": "COUNT_CLIENTES"},
    )
    router.route.return_value = HybridRouteOutcome(result=expected)
    business_understanding = MagicMock()
    business_understanding.understand.return_value = MagicMock()
    business_resolution = MagicMock()
    business_resolution.resolve.return_value = MagicMock()
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

    result = capability.execute("cuantos clientes existen", session_id="sess-42")

    conversation_context.prepare_session.assert_called_once_with(
        "cuantos clientes existen",
        "sess-42",
    )
    conversation_context.resolve.assert_called_once()
    business_understanding.understand.assert_called_once_with("cuantos clientes existen")
    business_resolution.resolve.assert_called_once()
    router.route.assert_called_once()
    assert router.route.call_args.kwargs["pipeline_state"].session_id is not None
    assert result is expected
