from collections.abc import Callable

from app.conversation_memory.schemas import ConversationContext
from app.query_engine.query_catalog import (
    DEFAULT_TOP_QUESTIONS,
    DISCOVERY_QUESTIONS,
    QUERY_TYPE_EXAMPLE_QUESTIONS,
    RELATED_QUERY_TYPES,
)
from app.query_engine.query_types import BusinessQueryType
from app.suggested_questions.rules import (
    CAPABILITY_DISCOVERY_RULES,
    GUIDED_FALLBACK_RULES,
    TYPE_SPECIFIC_RULES,
)
from app.suggested_questions.schemas import SuggestedQuestionsResult
from app.suggested_questions.validator import validate_questions

TopQuestionsProvider = Callable[[int], list[str]]

MIN_SUGGESTIONS = 3
MAX_SUGGESTIONS = 5


class SuggestedQuestionsEngine:
    """Genera próximos pasos conversacionales determinísticos."""

    def __init__(
        self,
        top_questions_provider: TopQuestionsProvider | None = None,
    ) -> None:
        self._top_questions_provider = top_questions_provider or (
            lambda limit: list(DEFAULT_TOP_QUESTIONS[:limit])
        )

    def generate(
        self,
        *,
        current_query_type: str | None = None,
        current_operation: str | None = None,
        current_entity: str | None = None,
        conversation_context: ConversationContext | None = None,
        handled_by: str | None = None,
        confidence: float | None = None,
    ) -> SuggestedQuestionsResult:
        query_type = self._resolve_query_type(current_query_type, handled_by)
        candidates: list[str] = []
        source_parts: list[str] = []

        if handled_by == "capability_discovery":
            candidates.extend(CAPABILITY_DISCOVERY_RULES)
            source_parts.append("capability_discovery")
        elif handled_by == "guided_fallback":
            candidates.extend(GUIDED_FALLBACK_RULES)
            source_parts.append("guided_fallback")
        elif query_type in TYPE_SPECIFIC_RULES:
            candidates.extend(TYPE_SPECIFIC_RULES[query_type])
            source_parts.append("type_rules")

        for question in self._top_questions_provider(MAX_SUGGESTIONS):
            candidates.append(question)
        if not source_parts or source_parts[-1] != "top_queries":
            source_parts.append("top_queries")

        for related in RELATED_QUERY_TYPES.get(query_type, ()):
            example = QUERY_TYPE_EXAMPLE_QUESTIONS.get(related)
            if example:
                candidates.append(example)
        source_parts.append("related_types")

        for example in QUERY_TYPE_EXAMPLE_QUESTIONS.values():
            candidates.append(example)
        source_parts.append("capabilities")

        for question in DISCOVERY_QUESTIONS:
            candidates.append(question)
        source_parts.append("discovery")

        if conversation_context and conversation_context.last_query_type:
            _ = conversation_context.last_query_type

        _ = current_operation
        _ = current_entity

        questions = validate_questions(candidates)[:MAX_SUGGESTIONS]
        while len(questions) < MIN_SUGGESTIONS:
            for fallback in DEFAULT_TOP_QUESTIONS:
                extra = validate_questions([fallback])
                for item in extra:
                    if item not in questions:
                        questions.append(item)
                if len(questions) >= MIN_SUGGESTIONS:
                    break
            break

        questions = questions[:MAX_SUGGESTIONS]
        resolved_confidence = confidence if confidence is not None else 0.85

        return SuggestedQuestionsResult(
            questions=questions,
            source=source_parts[0] if len(source_parts) == 1 else "mixed",
            confidence=resolved_confidence,
            metadata={
                "suggested_questions_count": len(questions),
                "query_type": current_query_type,
                "handled_by": handled_by,
                "source_parts": source_parts,
            },
        )

    @staticmethod
    def _resolve_query_type(
        current_query_type: str | None,
        handled_by: str | None,
    ) -> BusinessQueryType | None:
        if handled_by == "capability_discovery":
            return None
        if handled_by == "guided_fallback":
            return None
        if not current_query_type:
            return None
        try:
            return BusinessQueryType(current_query_type)
        except ValueError:
            return None
