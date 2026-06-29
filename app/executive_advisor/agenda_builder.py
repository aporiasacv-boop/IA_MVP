from collections.abc import Callable
from typing import Any

from app.conversation_memory.service import ConversationMemoryService
from app.executive_advisor.schemas import AdvisorInput
from app.schemas.hybrid_chat import HybridChatResult
from app.simulation_engine.scenario_engine import PREDEFINED_SCENARIOS


DatasetSummaryProvider = Callable[[], dict]
TopQueriesProvider = Callable[[int], list[dict[str, Any]]]
CoverageReportProvider = Callable[[], dict[str, Any]]


def build_advisor_input(
    *,
    dataset_summary_provider: DatasetSummaryProvider | None = None,
    top_queries_provider: TopQueriesProvider | None = None,
    coverage_report_provider: CoverageReportProvider | None = None,
    conversation_memory_service: ConversationMemoryService | None = None,
    session_id: str | None = None,
    hybrid_result: HybridChatResult | None = None,
    recent_queries: list[str] | None = None,
    period: str | None = None,
    scenario: str | None = None,
) -> AdvisorInput:
    dataset_summary = _safe_call(dataset_summary_provider)
    operational_report = _safe_call(coverage_report_provider)
    top_queries_raw = _safe_call(top_queries_provider, 5) if top_queries_provider else []

    recent = list(recent_queries or [])
    for item in top_queries_raw or []:
        question = str(item.get("question", "")).strip()
        if question and question not in recent:
            recent.append(question)

    conversation_context = None
    if conversation_memory_service and session_id:
        context = conversation_memory_service.get_context(session_id)
        if context is not None:
            conversation_context = {
                "turn_count": context.turn_count,
                "last_query_type": context.last_query_type,
                "last_filters": context.last_filters,
            }

    executive_insight = None
    copilot_proposals: list[dict] = []
    last_query_type = None
    last_answer = None

    if hybrid_result is not None:
        metadata = hybrid_result.metadata
        raw_insight = metadata.get("executive_insight")
        if isinstance(raw_insight, dict):
            executive_insight = raw_insight
        raw_proposals = metadata.get("business_copilot_proposals")
        if isinstance(raw_proposals, list):
            copilot_proposals = [item for item in raw_proposals if isinstance(item, dict)]
        last_query_type = str(metadata.get("query_type", "")).upper() or None
        last_answer = hybrid_result.answer

    financial_scenario = _resolve_financial_scenario(scenario)

    temporal_coverage = None
    if dataset_summary:
        temporal_coverage = {
            "fecha_minima": dataset_summary.get("fecha_minima"),
            "fecha_maxima": dataset_summary.get("fecha_maxima"),
            "meses": dataset_summary.get("meses"),
            "anios": dataset_summary.get("anios"),
        }

    return AdvisorInput(
        dataset_summary=dataset_summary,
        temporal_coverage=temporal_coverage,
        executive_insight=executive_insight,
        business_copilot_proposals=copilot_proposals,
        conversation_context=conversation_context,
        recent_queries=recent[:10],
        financial_scenario=financial_scenario,
        operational_report=operational_report,
        last_query_type=last_query_type,
        last_answer=last_answer,
        period=period,
        scenario=scenario,
    )


def advisor_input_to_prompt_dict(advisor_input: AdvisorInput) -> dict:
    return advisor_input.model_dump(exclude_none=True)


def _resolve_financial_scenario(scenario_id: str | None) -> dict | None:
    if not PREDEFINED_SCENARIOS:
        return None

    selected = None
    if scenario_id:
        selected = next(
            (item for item in PREDEFINED_SCENARIOS if item.id == scenario_id),
            None,
        )
    if selected is None:
        selected = max(
            PREDEFINED_SCENARIOS,
            key=lambda item: item.defaults.users,
        )

    return {
        "id": selected.id,
        "name": selected.name,
        "description": selected.description,
        "users": selected.defaults.users,
        "queries_per_user_day": selected.defaults.queries_per_user_day,
    }


def _safe_call(provider: Callable[..., Any] | None, *args: Any) -> Any:
    if provider is None:
        return None
    try:
        return provider(*args)
    except Exception:
        return None
