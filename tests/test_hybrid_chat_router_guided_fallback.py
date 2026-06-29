from unittest.mock import MagicMock

from app.capabilities.business_pipeline_state import BusinessPipelineState
from app.capabilities.guided_fallback_capability import GuidedFallbackStage
from app.conversation_memory.schemas import ConversationContext
from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_types import BusinessQueryType
from app.schemas.hybrid_chat import HybridChatResult
from app.services.hybrid_chat_router import HybridChatRouter
from app.capabilities.business_understanding_capability import (
    BusinessUnderstandingResult,
    BusinessUnderstandingStage,
)


def test_route_returns_precomputed_guided_fallback() -> None:
    legacy_handler = MagicMock()
    router = HybridChatRouter(legacy_handler)
    fallback_result = HybridChatResult(
        handled_by="guided_fallback",
        success=True,
        answer="Puedo ayudarte con consultas de clientes.",
        metadata={"handled_by": "guided_fallback", "fallback_type": "UNKNOWN"},
    )
    pipeline_state = BusinessPipelineState(
        session_id="sess-fallback",
        context=ConversationContext(session_id="sess-fallback"),
        memory_resolution=None,
        business_understanding=BusinessUnderstandingStage(
            result=BusinessUnderstandingResult(
                intent=MagicMock(confidence=0.4),
                query=BusinessQuery(query_type=BusinessQueryType.UNSUPPORTED),
            ),
            intent_stage_ms=1.0,
            planner_stage_ms=1.0,
        ),
        guided_fallback=GuidedFallbackStage(
            result=fallback_result,
            stage_ms=8.0,
        ),
    )

    outcome = router.route("¿Cómo va el negocio?", pipeline_state=pipeline_state)

    assert outcome.result is fallback_result
    legacy_handler.assert_not_called()
