import time

from app.ai_orchestration.providers.base import BaseLLMProvider
from app.core.settings import settings
from app.executive_advisor.agenda_builder import advisor_input_to_prompt_dict
from app.executive_advisor.fallback import build_greeting, build_rule_based_agenda
from app.executive_advisor.metrics import record_advisor_metrics
from app.executive_advisor.parser import parse_advisor_response
from app.executive_advisor.priority_engine import boost_from_copilot, prioritize_agenda
from app.executive_advisor.prompt import build_executive_advisor_prompt
from app.executive_advisor.schemas import AdvisorInput, ExecutiveAgenda, ExecutiveAgendaResponse
from app.schemas.hybrid_chat import HybridChatResult
from app.utils.text_normalizer import normalize_for_matching


class ExecutiveAdvisorEngine:

    def __init__(
        self,
        llm_provider: BaseLLMProvider | None = None,
        *,
        enabled: bool | None = None,
    ) -> None:
        self._llm_provider = llm_provider
        self._enabled = settings.EXECUTIVE_ADVISOR_ENABLED if enabled is None else enabled

    def build_agenda(self, advisor_input: AdvisorInput) -> ExecutiveAgendaResponse:
        started = time.perf_counter()
        provider = self._resolve_provider()
        provider_name = provider.provider_name()
        model_name = provider.model_name
        fallback_used = True
        agenda: ExecutiveAgenda | None = None

        if self._enabled:
            prompt = build_executive_advisor_prompt(
                advisor_input_to_prompt_dict(advisor_input),
            )
            try:
                llm_result = provider.generate_response(prompt)
                provider_name = llm_result.provider or provider_name
                model_name = llm_result.model or model_name
                agenda = parse_advisor_response(llm_result.text or "")
                if agenda is not None:
                    fallback_used = False
            except Exception:
                agenda = None

        if agenda is None:
            agenda = build_rule_based_agenda(advisor_input)
            fallback_used = True

        agenda = prioritize_agenda(agenda)
        agenda = ExecutiveAgenda(
            greeting=agenda.greeting or build_greeting(),
            items=boost_from_copilot(list(agenda.items), advisor_input.business_copilot_proposals),
        )
        agenda = prioritize_agenda(agenda)
        agenda = _filter_recent_queries(agenda, advisor_input.recent_queries)

        if not agenda.items:
            agenda = build_rule_based_agenda(advisor_input)
            fallback_used = True

        generation_ms = (time.perf_counter() - started) * 1000
        record_advisor_metrics(
            generated=bool(agenda.items),
            fallback=fallback_used,
            generation_ms=generation_ms,
            items=len(agenda.items),
        )

        return ExecutiveAgendaResponse(
            agenda=agenda,
            advisor_generation_ms=round(generation_ms, 2),
            advisor_provider=provider_name,
            advisor_model=model_name,
            advisor_items=len(agenda.items),
            advisor_fallback_used=fallback_used,
        )

    def enrich(
        self,
        advisor_input: AdvisorInput,
        result: HybridChatResult,
    ) -> HybridChatResult:
        if not self._enabled or not result.success:
            return result

        response = self.build_agenda(advisor_input)
        if not response.agenda.items:
            return result

        return HybridChatResult(
            handled_by=result.handled_by,
            success=result.success,
            answer=result.answer,
            suggestions=result.suggestions,
            metadata={
                **result.metadata,
                "executive_advisor_agenda": response.agenda.model_dump(),
                "advisor_generation_ms": response.advisor_generation_ms,
                "advisor_provider": response.advisor_provider,
                "advisor_model": response.advisor_model,
                "advisor_items": response.advisor_items,
                "advisor_fallback_used": response.advisor_fallback_used,
            },
        )

    def _resolve_provider(self) -> BaseLLMProvider:
        if self._llm_provider is None:
            from app.ai_orchestration.providers.factory import create_llm_provider_with_fallback

            self._llm_provider = create_llm_provider_with_fallback()
        return self._llm_provider


def _filter_recent_queries(
    agenda: ExecutiveAgenda,
    recent_queries: list[str],
) -> ExecutiveAgenda:
    blocked = {normalize_for_matching(query) for query in recent_queries}
    items = [
        item
        for item in agenda.items
        if normalize_for_matching(item.suggested_query) not in blocked
    ]
    return ExecutiveAgenda(greeting=agenda.greeting, items=items)
