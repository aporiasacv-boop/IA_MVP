import time

from app.ai_orchestration.providers.base import BaseLLMProvider
from app.business_copilot.constants import (
    COPILOT_ELIGIBLE_HANDLED_BY,
    COPILOT_ELIGIBLE_QUERY_TYPES,
)
from app.business_copilot.fallback import build_rule_based_proposals
from app.business_copilot.metrics import record_copilot_metrics
from app.business_copilot.parser import parse_copilot_response
from app.business_copilot.prompt import build_business_copilot_prompt
from app.business_copilot.schemas import CopilotPayload
from app.conversation_memory.service import ConversationMemoryService
from app.core.settings import settings
from app.schemas.hybrid_chat import HybridChatResult
from app.utils.text_normalizer import normalize_for_matching


class BusinessCopilotEngine:

    def __init__(
        self,
        llm_provider: BaseLLMProvider | None = None,
        *,
        enabled: bool | None = None,
        conversation_memory_service: ConversationMemoryService | None = None,
    ) -> None:
        self._llm_provider = llm_provider
        self._enabled = settings.BUSINESS_COPILOT_ENABLED if enabled is None else enabled
        self._conversation_memory_service = (
            conversation_memory_service or ConversationMemoryService()
        )
        self._session_questions: dict[str, list[str]] = {}

    def enrich(
        self,
        user_question: str,
        result: HybridChatResult,
        *,
        session_id: str | None = None,
    ) -> HybridChatResult:
        if not self._enabled or not result.success:
            return result

        if result.handled_by not in COPILOT_ELIGIBLE_HANDLED_BY:
            return result

        query_type = str(result.metadata.get("query_type", "")).upper()
        if result.handled_by != "executive_reasoning" and query_type not in COPILOT_ELIGIBLE_QUERY_TYPES:
            return result

        prior_questions = self._prior_questions(session_id, user_question)
        existing_suggestions = list(result.suggestions.questions) if result.suggestions else []
        executive_insight = result.metadata.get("executive_insight")
        insight_dict = executive_insight if isinstance(executive_insight, dict) else None

        started = time.perf_counter()
        provider = self._resolve_provider()
        prompt = build_business_copilot_prompt(
            user_question=user_question,
            query_type=query_type,
            deterministic_answer=result.answer,
            executive_insight=insight_dict,
            existing_suggestions=existing_suggestions,
            prior_questions=prior_questions,
            conversation_context=self._conversation_context(session_id),
        )

        payload: CopilotPayload | None = None
        llm_fallback = True
        provider_name = provider.provider_name()
        model_name = provider.model_name

        try:
            llm_result = provider.generate_response(prompt)
            provider_name = llm_result.provider or provider_name
            model_name = llm_result.model or model_name
            payload = parse_copilot_response(llm_result.text or "")
            if payload is not None and payload.proposals:
                payload = _filter_payload(payload, prior_questions, existing_suggestions)
                if payload.proposals:
                    llm_fallback = False
        except Exception:
            payload = None

        if payload is None or not payload.proposals:
            payload = build_rule_based_proposals(
                query_type=query_type,
                handled_by=result.handled_by,
                prior_questions=prior_questions,
            )
            payload = _filter_payload(payload, prior_questions, existing_suggestions)
            fallback_used = True
        else:
            fallback_used = llm_fallback

        generation_ms = (time.perf_counter() - started) * 1000
        proposals_generated = bool(payload.proposals)

        record_copilot_metrics(
            generated=proposals_generated,
            fallback=fallback_used or not proposals_generated,
            generation_ms=generation_ms,
        )

        self._record_question(session_id, user_question)

        if proposals_generated:
            self._record_proposal_queries(session_id, payload.proposals)

        if not proposals_generated:
            return HybridChatResult(
                handled_by=result.handled_by,
                success=result.success,
                answer=result.answer,
                suggestions=result.suggestions,
                metadata={
                    **result.metadata,
                    "copilot_generation_ms": round(generation_ms, 2),
                    "copilot_provider": provider_name,
                    "copilot_model": model_name,
                    "proposals_generated": False,
                    "copilot_fallback_used": True,
                },
            )

        return HybridChatResult(
            handled_by=result.handled_by,
            success=result.success,
            answer=result.answer,
            suggestions=result.suggestions,
            metadata={
                **result.metadata,
                "business_copilot_proposals": [
                    proposal.model_dump() for proposal in payload.proposals
                ],
                "copilot_generation_ms": round(generation_ms, 2),
                "copilot_provider": provider_name,
                "copilot_model": model_name,
                "proposals_generated": True,
                "copilot_fallback_used": fallback_used,
            },
        )

    def _resolve_provider(self) -> BaseLLMProvider:
        if self._llm_provider is None:
            from app.ai_orchestration.providers.factory import create_llm_provider_with_fallback

            self._llm_provider = create_llm_provider_with_fallback()
        return self._llm_provider

    def _prior_questions(self, session_id: str | None, current_question: str) -> list[str]:
        history = list(self._session_questions.get(session_id or "", []))
        normalized_current = normalize_for_matching(current_question)
        return [
            question
            for question in history
            if normalize_for_matching(question) != normalized_current
        ]

    def _record_question(self, session_id: str | None, question: str) -> None:
        if not session_id:
            return
        trimmed = question.strip()
        if not trimmed:
            return
        history = self._session_questions.setdefault(session_id, [])
        if normalize_for_matching(trimmed) not in {
            normalize_for_matching(item) for item in history
        }:
            history.append(trimmed)

    def _record_proposal_queries(self, session_id: str | None, proposals) -> None:
        for proposal in proposals:
            self._record_question(session_id, proposal.query)

    def _conversation_context(self, session_id: str | None) -> dict | None:
        if not session_id:
            return None
        context = self._conversation_memory_service.get_context(session_id)
        if context is None:
            return None
        return {
            "turn_count": context.turn_count,
            "last_query_type": context.last_query_type,
            "last_filters": context.last_filters,
        }


def _filter_payload(
    payload: CopilotPayload,
    prior_questions: list[str],
    existing_suggestions: list[str],
) -> CopilotPayload:
    blocked = {
        normalize_for_matching(question)
        for question in [*prior_questions, *existing_suggestions]
    }
    proposals = [
        proposal
        for proposal in payload.proposals
        if normalize_for_matching(proposal.query) not in blocked
    ]
    return CopilotPayload(proposals=proposals)
