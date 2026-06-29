import time
from dataclasses import dataclass

from app.conversation_memory.schemas import ConversationContext
from app.guided_fallback.engine import GuidedFallbackEngine
from app.guided_fallback.schemas import GuidedFallbackResult
from app.observability.performance_metrics import elapsed_ms
from app.query_engine.business_query import BusinessQuery
from app.schemas.hybrid_chat import HybridChatResult
from app.schemas.semantic_intent import BusinessSemanticIntent


@dataclass(frozen=True)
class GuidedFallbackStage:
    """Resultado de fallback guiado con tiempo de etapa para el pipeline."""

    result: HybridChatResult
    stage_ms: float


class GuidedFallbackCapability:
    """Ejecuta recuperación guiada cuando la consulta no puede resolverse determinísticamente."""

    HANDLED_BY = "guided_fallback"

    def __init__(self, engine: GuidedFallbackEngine | None = None) -> None:
        self._engine = engine or GuidedFallbackEngine()

    def try_fallback(
        self,
        message: str,
        semantic_intent: BusinessSemanticIntent,
        business_query: BusinessQuery,
        conversation_context: ConversationContext,
        *,
        session_id: str,
    ) -> GuidedFallbackStage | None:
        started = time.perf_counter()
        fallback = self._engine.resolve(
            message,
            semantic_intent,
            business_query,
            conversation_context,
        )
        stage_ms = elapsed_ms(started)
        if fallback is None:
            return None

        return GuidedFallbackStage(
            result=self._to_hybrid_chat_result(fallback, session_id=session_id),
            stage_ms=stage_ms,
        )

    def _to_hybrid_chat_result(
        self,
        fallback: GuidedFallbackResult,
        *,
        session_id: str,
    ) -> HybridChatResult:
        return HybridChatResult(
            handled_by=self.HANDLED_BY,
            success=fallback.success,
            answer=fallback.answer,
            metadata={
                "handled_by": self.HANDLED_BY,
                "fallback_type": fallback.fallback_type,
                "suggested_questions": fallback.suggested_questions,
                "suggested_questions_count": len(fallback.suggested_questions),
                "fallback_success": fallback.metadata.get("fallback_success", True),
                "session_id": session_id,
                **fallback.metadata,
            },
        )
