import time

from app.ai_orchestration.providers.base import BaseLLMProvider
from app.core.settings import settings
from app.executive_insight.constants import (
    INSIGHT_ELIGIBLE_HANDLED_BY,
    INSIGHT_ELIGIBLE_QUERY_TYPES,
)
from app.executive_insight.metrics import record_insight_metrics
from app.executive_insight.parser import parse_insight_response
from app.executive_insight.prompt import build_executive_insight_prompt
from app.executive_insight.schemas import ExecutiveInsightPayload
from app.schemas.hybrid_chat import HybridChatResult
from app.suggested_questions.schemas import SuggestedQuestionsResult


class ExecutiveInsightEngine:

    def __init__(
        self,
        llm_provider: BaseLLMProvider | None = None,
        *,
        enabled: bool | None = None,
    ) -> None:
        self._llm_provider = llm_provider
        self._enabled = settings.EXECUTIVE_INSIGHT_ENABLED if enabled is None else enabled

    def enrich(
        self,
        user_question: str,
        result: HybridChatResult,
        *,
        session_id: str | None = None,
    ) -> HybridChatResult:
        if not self._enabled or not result.success:
            return result

        if result.metadata.get("executive_reasoning_v2_enabled"):
            return result

        if result.handled_by not in INSIGHT_ELIGIBLE_HANDLED_BY:
            return result

        query_type = str(result.metadata.get("query_type", "")).upper()
        if query_type not in INSIGHT_ELIGIBLE_QUERY_TYPES:
            return result

        deterministic_answer = result.answer
        started = time.perf_counter()
        provider = self._resolve_provider()
        prompt = build_executive_insight_prompt(
            user_question=user_question,
            query_type=query_type,
            deterministic_answer=deterministic_answer,
            confidence=_as_float(result.metadata.get("confidence")),
            dataset_snapshot=_extract_dataset_snapshot(result.metadata),
        )

        insight: ExecutiveInsightPayload | None = None
        fallback_used = True
        provider_name = provider.provider_name()
        model_name = provider.model_name

        try:
            llm_result = provider.generate_response(prompt)
            provider_name = llm_result.provider or provider_name
            model_name = llm_result.model or model_name
            insight = parse_insight_response(llm_result.text or "")
            if insight is not None:
                fallback_used = False
        except Exception:
            insight = None

        generation_ms = (time.perf_counter() - started) * 1000
        insight_generated = insight is not None and _has_content(insight)

        record_insight_metrics(
            generated=insight_generated,
            fallback=fallback_used or not insight_generated,
            generation_ms=generation_ms,
        )

        if not insight_generated or insight is None:
            return HybridChatResult(
                handled_by=result.handled_by,
                success=result.success,
                answer=deterministic_answer,
                suggestions=result.suggestions,
                metadata={
                    **result.metadata,
                    "insight_generation_ms": round(generation_ms, 2),
                    "provider": provider_name,
                    "model": model_name,
                    "insight_generated": False,
                    "fallback_used": True,
                },
            )

        suggestions = _merge_suggestions(result.suggestions, insight.next_questions)

        return HybridChatResult(
            handled_by=result.handled_by,
            success=result.success,
            answer=deterministic_answer,
            suggestions=suggestions,
            metadata={
                **result.metadata,
                "executive_insight": insight.model_dump(),
                "insight_generation_ms": round(generation_ms, 2),
                "provider": provider_name,
                "model": model_name,
                "insight_generated": True,
                "fallback_used": fallback_used,
            },
        )

    def _resolve_provider(self) -> BaseLLMProvider:
        if self._llm_provider is None:
            from app.ai_orchestration.providers.factory import create_llm_provider_with_fallback

            self._llm_provider = create_llm_provider_with_fallback()
        return self._llm_provider


def _has_content(insight: ExecutiveInsightPayload) -> bool:
    return bool(
        insight.executive_summary
        or insight.business_interpretation
        or insight.possible_risks
        or insight.recommendations
        or insight.next_questions
    )


def _merge_suggestions(
    current: SuggestedQuestionsResult | None,
    next_questions: list[str],
) -> SuggestedQuestionsResult | None:
    if not next_questions:
        return current
    existing = list(current.questions) if current else []
    merged: list[str] = []
    seen: set[str] = set()
    for question in [*next_questions, *existing]:
        trimmed = question.strip()
        if not trimmed or trimmed in seen:
            continue
        seen.add(trimmed)
        merged.append(trimmed)
    return SuggestedQuestionsResult(
        questions=merged[:8],
        source=current.source if current else "executive_insight",
        confidence=current.confidence if current else 0.85,
        metadata=current.metadata if current else {},
    )


def _as_float(value: object) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _extract_dataset_snapshot(metadata: dict) -> dict | None:
    snapshot = metadata.get("dataset_snapshot")
    if isinstance(snapshot, dict):
        return snapshot
    conversation_snapshot = metadata.get("conversation_dataset_snapshot")
    if isinstance(conversation_snapshot, dict):
        return conversation_snapshot
    return None
