import time

from app.conversation_ux.classifier import ConversationCategory, greeting_time_phrase
from app.conversation_ux.context import DatasetSnapshot
from app.core.settings import settings
from app.enterprise_personality.adaptation import resolve_adaptation_type
from app.enterprise_personality.constants import (
    PROFILE_ENTERPRISE_INTELLIGENCE_DIRECTOR,
    PROTECTED_HANDLED_BY,
)
from app.enterprise_personality.metrics import record_personality
from app.enterprise_personality.voice import render_personality_answer, sanitize_personality_text
from app.schemas.hybrid_chat import HybridChatResult
from app.suggested_questions.schemas import SuggestedQuestionsResult


class EnterprisePersonalityEngine:
    """Aplica la personalidad oficial de Olnatura Intelligence a respuestas conversacionales."""

    def apply(
        self,
        message: str,
        result: HybridChatResult,
        *,
        conversation_turn: int = 0,
    ) -> HybridChatResult:
        started = time.perf_counter()

        if not settings.ENTERPRISE_PERSONALITY_ENABLED:
            return self._without_personality(result, started)

        if not result.metadata.get("conversation_ux_applied"):
            return self._without_personality(result, started)

        if result.handled_by in PROTECTED_HANDLED_BY:
            return self._without_personality(result, started)

        category = self._resolve_category(result)
        if category is ConversationCategory.NONE:
            return self._without_personality(result, started)

        adaptation_type = resolve_adaptation_type(
            category,
            conversation_turn=conversation_turn,
        )
        snapshot = self._resolve_snapshot(result)
        capabilities = self._string_list(result.metadata.get("conversation_capabilities"))
        examples = self._string_list(result.metadata.get("conversation_capability_examples"))

        greeting = greeting_time_phrase(message) if category is ConversationCategory.GREETING else ""
        answer = render_personality_answer(
            category=category,
            adaptation_type=adaptation_type,
            greeting=greeting,
            snapshot=snapshot,
            capability_labels=capabilities,
            example_questions=examples,
        )
        if not answer:
            return self._without_personality(result, started)

        answer = sanitize_personality_text(answer)
        elapsed_ms = (time.perf_counter() - started) * 1000
        record_personality(time_ms=elapsed_ms)

        suggestions = self._with_personality_suggestions(result.suggestions, category)

        return HybridChatResult(
            handled_by=result.handled_by,
            success=result.success,
            answer=answer,
            suggestions=suggestions,
            metadata={
                **result.metadata,
                "personality_applied": True,
                "personality_profile": PROFILE_ENTERPRISE_INTELLIGENCE_DIRECTOR,
                "adaptation_type": adaptation_type,
                "personality_time_ms": round(elapsed_ms, 2),
                "conversation_personality_answer": answer,
                "conversation_template_answer": result.metadata.get(
                    "conversation_template_answer",
                    result.answer,
                ),
                "conversation_ux_layer": "personality_v1",
            },
        )

    @staticmethod
    def _without_personality(result: HybridChatResult, started: float) -> HybridChatResult:
        elapsed_ms = (time.perf_counter() - started) * 1000
        return HybridChatResult(
            handled_by=result.handled_by,
            success=result.success,
            answer=result.answer,
            suggestions=result.suggestions,
            metadata={
                **result.metadata,
                "personality_applied": False,
                "personality_profile": PROFILE_ENTERPRISE_INTELLIGENCE_DIRECTOR,
                "adaptation_type": None,
                "personality_time_ms": round(elapsed_ms, 2),
            },
        )

    @staticmethod
    def _resolve_category(result: HybridChatResult) -> ConversationCategory:
        raw = result.metadata.get("conversation_category", ConversationCategory.NONE.value)
        try:
            return ConversationCategory(raw)
        except ValueError:
            return ConversationCategory.NONE

    @staticmethod
    def _resolve_snapshot(result: HybridChatResult) -> DatasetSnapshot:
        snapshot_data = result.metadata.get("conversation_dataset_snapshot", {})
        if not isinstance(snapshot_data, dict):
            return DatasetSnapshot.empty()
        return DatasetSnapshot.from_mapping(snapshot_data)

    @staticmethod
    def _string_list(value: object) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item) for item in value if str(item).strip()]

    @staticmethod
    def _with_personality_suggestions(
        suggestions: SuggestedQuestionsResult | None,
        category: ConversationCategory,
    ) -> SuggestedQuestionsResult | None:
        if suggestions is None:
            return None

        metadata = {
            **suggestions.metadata,
            "personality_suggestions_profile": PROFILE_ENTERPRISE_INTELLIGENCE_DIRECTOR,
            "personality_suggestions_category": category.value,
        }
        return SuggestedQuestionsResult(
            questions=suggestions.questions,
            source=suggestions.source,
            confidence=suggestions.confidence,
            metadata=metadata,
        )
