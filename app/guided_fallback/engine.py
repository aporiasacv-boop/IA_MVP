from collections.abc import Callable

from app.conversation_memory.schemas import ConversationContext
from app.guided_fallback.classifier import classify_fallback_type
from app.guided_fallback.schemas import GuidedFallbackResult
from app.guided_fallback.suggested_questions import (
    DEFAULT_TOP_QUESTIONS,
    TopQuestionsProvider,
    build_suggested_questions,
)
from app.guided_fallback.templates import (
    AMBIGUOUS_FOOTER,
    AMBIGUOUS_HEADER,
    AMBIGUOUS_OPTIONS,
    LOW_CONFIDENCE_HEADER,
    OUT_OF_DOMAIN_ANSWER,
    UNKNOWN_CAPABILITIES,
    UNKNOWN_HEADER,
    UNSUPPORTED_CAPABILITY_HEADER,
)
from app.guided_fallback.types import FallbackType
from app.guided_fallback.v2.detector import detect_domain
from app.guided_fallback.v2.formatter import build_domain_contextual_answer
from app.guided_fallback.v2.metrics import GuidedFallbackV2Metrics
from app.query_engine.business_query import BusinessQuery
from app.schemas.semantic_intent import BusinessSemanticIntent
from app.suggested_questions.engine import SuggestedQuestionsEngine


class GuidedFallbackEngine:
    """Orienta al usuario cuando el pipeline empresarial no puede ejecutar la consulta."""

    def __init__(
        self,
        top_questions_provider: TopQuestionsProvider | None = None,
    ) -> None:
        self._top_questions_provider = top_questions_provider or (
            lambda limit: list(DEFAULT_TOP_QUESTIONS[:limit])
        )

    def resolve(
        self,
        question: str,
        semantic_intent: BusinessSemanticIntent,
        business_query: BusinessQuery,
        conversation_context: ConversationContext | None,
    ) -> GuidedFallbackResult | None:
        fallback_type = classify_fallback_type(
            question,
            semantic_intent,
            business_query,
            conversation_context,
        )
        if fallback_type is None:
            return None

        suggested_questions = build_suggested_questions(
            top_questions_provider=self._top_questions_provider,
        )
        domain = detect_domain(question)
        use_domain_context = domain is not None and fallback_type != FallbackType.OUT_OF_DOMAIN

        if use_domain_context:
            answer = build_domain_contextual_answer(domain)
            GuidedFallbackV2Metrics.record_hit(domain)
        else:
            answer = self._build_answer(fallback_type, suggested_questions)
            GuidedFallbackV2Metrics.record_miss()

        suggestions = SuggestedQuestionsEngine(
            top_questions_provider=self._top_questions_provider,
        ).generate(
            current_query_type=fallback_type.value,
            handled_by="guided_fallback",
            confidence=semantic_intent.confidence,
        )

        return GuidedFallbackResult(
            success=True,
            answer=answer,
            fallback_type=fallback_type.value,
            suggested_questions=suggested_questions,
            suggestions=suggestions,
            metadata={
                "fallback_success": True,
                "fallback_version": "v2" if use_domain_context else "v1",
                "domain_detected": domain.value if domain is not None else None,
                "domain_contextual": use_domain_context,
                "suggested_questions_count": len(suggested_questions),
                "confidence": semantic_intent.confidence,
                "source_question": question,
                "operation": (
                    semantic_intent.operation.value
                    if semantic_intent.operation is not None
                    else None
                ),
                "target_entity": (
                    semantic_intent.target_entity.value
                    if semantic_intent.target_entity is not None
                    else None
                ),
            },
        )

    @staticmethod
    def _build_answer(
        fallback_type: FallbackType,
        suggested_questions: list[str],
    ) -> str:
        if fallback_type == FallbackType.OUT_OF_DOMAIN:
            return OUT_OF_DOMAIN_ANSWER

        if fallback_type == FallbackType.AMBIGUOUS:
            lines = [AMBIGUOUS_HEADER, ""]
            lines.extend(f"• {option}" for option in AMBIGUOUS_OPTIONS)
            lines.append("")
            lines.append(AMBIGUOUS_FOOTER)
            return "\n".join(lines)

        if fallback_type == FallbackType.UNKNOWN:
            lines = [UNKNOWN_HEADER, ""]
            lines.extend(f"• {item}" for item in UNKNOWN_CAPABILITIES)
            return "\n".join(lines)

        header = (
            LOW_CONFIDENCE_HEADER
            if fallback_type == FallbackType.LOW_CONFIDENCE
            else UNSUPPORTED_CAPABILITY_HEADER
        )
        lines = [header, ""]
        for question in suggested_questions:
            lines.append(f"• {question}")
        return "\n".join(lines)
