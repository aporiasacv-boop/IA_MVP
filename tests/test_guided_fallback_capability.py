from unittest.mock import MagicMock

from app.capabilities.guided_fallback_capability import GuidedFallbackCapability
from app.conversation_memory.schemas import ConversationContext
from app.guided_fallback.schemas import GuidedFallbackResult
from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_types import BusinessQueryType
from app.schemas.hybrid_chat import HybridChatResult


def test_try_fallback_returns_none_when_engine_has_no_match() -> None:
    engine = MagicMock()
    engine.resolve.return_value = None
    capability = GuidedFallbackCapability(engine=engine)
    context = ConversationContext(session_id="sess-1")

    result = capability.try_fallback(
        "pregunta ambigua",
        MagicMock(confidence=0.4),
        BusinessQuery(query_type=BusinessQueryType.UNSUPPORTED),
        context,
        session_id="sess-1",
    )

    assert result is None
    engine.resolve.assert_called_once()


def test_try_fallback_builds_hybrid_chat_result() -> None:
    engine = MagicMock()
    engine.resolve.return_value = GuidedFallbackResult(
        success=True,
        answer="Puedo ayudarte con clientes y proveedores.",
        fallback_type="UNKNOWN",
        suggested_questions=["¿Cuántos clientes existen?"],
        metadata={"fallback_success": True},
    )
    capability = GuidedFallbackCapability(engine=engine)
    context = ConversationContext(session_id="sess-2")

    stage = capability.try_fallback(
        "¿Qué puedes hacer?",
        MagicMock(confidence=0.5),
        BusinessQuery(query_type=BusinessQueryType.UNSUPPORTED),
        context,
        session_id="sess-2",
    )

    assert stage is not None
    assert stage.result.handled_by == "guided_fallback"
    assert stage.result.metadata["fallback_type"] == "UNKNOWN"
    assert stage.result.metadata["session_id"] == "sess-2"
    assert stage.stage_ms >= 0
