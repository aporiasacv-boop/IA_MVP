from unittest.mock import MagicMock

from app.capabilities.business_pipeline_state import BusinessPipelineState
from app.capabilities.executive_reasoning_capability import ExecutiveReasoningStage
from app.conversation_memory.schemas import ConversationContext
from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_types import BusinessQueryType
from app.schemas.hybrid_chat import HybridChatResult
from app.services.hybrid_chat_router import HybridChatRouter
from app.capabilities.business_understanding_capability import (
    BusinessUnderstandingResult,
    BusinessUnderstandingStage,
)


def test_route_returns_precomputed_executive_reasoning() -> None:
    legacy_handler = MagicMock()
    router = HybridChatRouter(legacy_handler)
    executive_result = HybridChatResult(
        handled_by="executive_reasoning",
        success=True,
        answer="Análisis ejecutivo.",
        metadata={"handled_by": "executive_reasoning"},
    )
    pipeline_state = BusinessPipelineState(
        session_id="sess-exec",
        context=ConversationContext(session_id="sess-exec"),
        memory_resolution=None,
        business_understanding=BusinessUnderstandingStage(
            result=BusinessUnderstandingResult(
                intent=MagicMock(confidence=0.9),
                query=BusinessQuery(query_type=BusinessQueryType.UNSUPPORTED),
            ),
            intent_stage_ms=1.0,
            planner_stage_ms=1.0,
        ),
        executive_reasoning=ExecutiveReasoningStage(
            result=executive_result,
            stage_ms=12.5,
        ),
    )

    outcome = router.route(
        "Evaluar riesgos del cliente principal",
        pipeline_state=pipeline_state,
    )

    assert outcome.result is executive_result
    legacy_handler.assert_not_called()
