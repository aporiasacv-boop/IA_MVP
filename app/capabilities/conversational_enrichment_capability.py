from app.conversation_memory.schemas import ConversationContext
from app.coverage_recovery.metrics import CoverageRecoveryMetricsService
from app.schemas.hybrid_chat import HybridChatResult
from app.suggested_questions.engine import SuggestedQuestionsEngine


class ConversationalEnrichmentCapability:
    """Enriquece respuestas con sugerencias y metadatos complementarios de cobertura."""

    _HANDLED_BY_CAPABILITY_DISCOVERY = "capability_discovery"

    def __init__(
        self,
        suggested_questions_engine: SuggestedQuestionsEngine | None = None,
    ) -> None:
        self._suggested_questions_engine = (
            suggested_questions_engine or SuggestedQuestionsEngine()
        )

    def enrich(
        self,
        result: HybridChatResult,
        *,
        context: ConversationContext,
    ) -> HybridChatResult:
        if result.handled_by == self._HANDLED_BY_CAPABILITY_DISCOVERY:
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
