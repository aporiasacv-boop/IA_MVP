import time
from typing import Any

from app.ai_orchestration.providers.base import BaseLLMProvider
from app.core.settings import settings
from app.enterprise_evidence_orchestrator.schemas import EnterpriseEvidencePackage
from app.executive_reasoning_v2.constants import (
    HANDLED_BY_EXECUTIVE_REASONING_V2,
)
from app.executive_reasoning_v2.metrics import record_reasoning_v2
from app.executive_reasoning_v2.parser import parse_reasoning_v2_response
from app.executive_reasoning_v2.prompt import build_executive_reasoning_v2_prompt
from app.executive_reasoning_v2.schemas import ExecutiveReasoningV2Payload
from app.schemas.hybrid_chat import HybridChatResult
from app.suggested_questions.schemas import SuggestedQuestionsResult


class ExecutiveReasoningV2Engine:
    """Razonamiento ejecutivo exclusivamente sobre Enterprise Evidence Package."""

    def __init__(
        self,
        llm_provider: BaseLLMProvider | None = None,
        *,
        enabled: bool | None = None,
    ) -> None:
        self._llm_provider = llm_provider
        self._enabled = settings.EXECUTIVE_REASONING_V2_ENABLED if enabled is None else enabled

    def enrich(
        self,
        user_question: str,
        result: HybridChatResult,
        *,
        session_id: str | None = None,
    ) -> HybridChatResult:
        _ = session_id
        if not self._enabled or not result.success:
            return result

        package = _parse_evidence_package(result.metadata)
        if package is None or not package.evidence_items:
            record_reasoning_v2(generated=False, skipped=True)
            return result

        business_goal = package.business_goal or str(result.metadata.get("business_goal", ""))
        conversation_context = _extract_conversation_context(result.metadata)
        original_answer = result.answer
        preserve_answer = _should_preserve_deterministic_answer(result, package)

        started = time.perf_counter()
        provider = self._resolve_provider()
        prompt = build_executive_reasoning_v2_prompt(
            original_question=user_question,
            business_goal=business_goal,
            evidence_package=package,
            conversation_context=conversation_context,
        )

        reasoning: ExecutiveReasoningV2Payload | None = None
        provider_name = provider.provider_name()
        model_name = provider.model_name

        try:
            llm_result = provider.generate_response(prompt)
            provider_name = llm_result.provider or provider_name
            model_name = llm_result.model or model_name
            reasoning = parse_reasoning_v2_response(llm_result.text or "")
        except Exception:
            reasoning = None

        generation_ms = (time.perf_counter() - started) * 1000
        generated = reasoning is not None and reasoning.has_content()
        record_reasoning_v2(
            generated=generated,
            skipped=False,
            fallback=not generated,
        )

        observability = {
            "executive_reasoning_v2_enabled": True,
            "evidence_package_used": True,
            "evidence_items_used": [item.evidence_id for item in package.evidence_items],
            "evidence_coverage": round(package.coverage, 2),
            "reasoning_generation_ms": round(generation_ms, 2),
            "reasoning_sections_generated": reasoning.generated_sections() if reasoning else [],
            "provider": provider_name,
            "model": model_name,
        }

        if not generated or reasoning is None:
            return HybridChatResult(
                handled_by=result.handled_by,
                success=result.success,
                answer=original_answer,
                suggestions=result.suggestions,
                metadata={
                    **result.metadata,
                    **observability,
                    "executive_reasoning_v2_generated": False,
                },
            )

        panel_payload = reasoning.to_panel_payload()
        answer = original_answer if preserve_answer else reasoning.to_executive_answer()
        handled_by = result.handled_by if preserve_answer else HANDLED_BY_EXECUTIVE_REASONING_V2
        suggestions = _merge_suggestions(result.suggestions, reasoning.next_analyses)

        return HybridChatResult(
            handled_by=handled_by,
            success=result.success,
            answer=answer,
            suggestions=suggestions,
            metadata={
                **result.metadata,
                **observability,
                "executive_reasoning_v2": reasoning.model_dump(),
                "executive_reasoning_v2_generated": True,
                "executive_insight": panel_payload,
                "insight_generated": True,
                "insight_source": "executive_reasoning_v2",
            },
        )

    def _resolve_provider(self) -> BaseLLMProvider:
        if self._llm_provider is None:
            from app.ai_orchestration.providers.factory import create_llm_provider_with_fallback

            self._llm_provider = create_llm_provider_with_fallback()
        return self._llm_provider


def _parse_evidence_package(metadata: dict[str, Any]) -> EnterpriseEvidencePackage | None:
    raw = metadata.get("enterprise_evidence_package")
    if not isinstance(raw, dict):
        return None
    try:
        return EnterpriseEvidencePackage.model_validate(raw)
    except Exception:
        return None


def _should_preserve_deterministic_answer(
    result: HybridChatResult,
    package: EnterpriseEvidencePackage,
) -> bool:
    _ = package
    if result.handled_by == "business_pipeline":
        return True
    if result.handled_by == "guided_fallback":
        return False
    return True


def _extract_conversation_context(metadata: dict[str, Any]) -> dict | None:
    context: dict[str, Any] = {}
    for key in (
        "reasoning_intent",
        "reasoning_explanation",
        "reasoning_route",
        "conversation_topic",
        "conversation_ux_applied",
    ):
        value = metadata.get(key)
        if value is not None:
            context[key] = value
    return context or None


def _merge_suggestions(
    current: SuggestedQuestionsResult | None,
    next_analyses: list[str],
) -> SuggestedQuestionsResult | None:
    if not next_analyses:
        return current
    existing = list(current.questions) if current else []
    merged: list[str] = []
    seen: set[str] = set()
    for question in [*next_analyses, *existing]:
        trimmed = question.strip()
        if not trimmed or trimmed in seen:
            continue
        seen.add(trimmed)
        merged.append(trimmed)
    return SuggestedQuestionsResult(
        questions=merged[:8],
        source=current.source if current else "executive_reasoning_v2",
        confidence=current.confidence if current else 0.85,
        metadata=current.metadata if current else {},
    )
