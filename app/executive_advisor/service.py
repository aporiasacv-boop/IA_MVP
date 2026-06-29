from app.executive_advisor.agenda_builder import build_advisor_input
from app.executive_advisor.engine import ExecutiveAdvisorEngine
from app.executive_advisor.schemas import ExecutiveAgendaResponse
from app.schemas.hybrid_chat import HybridChatResult


class ExecutiveAdvisorService:

    def __init__(
        self,
        *,
        advisor_engine: ExecutiveAdvisorEngine,
        dataset_summary_provider,
        top_queries_provider,
        coverage_report_provider,
        conversation_memory_service,
    ) -> None:
        self._advisor_engine = advisor_engine
        self._dataset_summary_provider = dataset_summary_provider
        self._top_queries_provider = top_queries_provider
        self._coverage_report_provider = coverage_report_provider
        self._conversation_memory_service = conversation_memory_service

    def get_agenda(
        self,
        *,
        session_id: str | None = None,
        period: str | None = None,
        scenario: str | None = None,
        recent_queries: list[str] | None = None,
    ) -> ExecutiveAgendaResponse:
        advisor_input = build_advisor_input(
            dataset_summary_provider=self._dataset_summary_provider,
            top_queries_provider=self._top_queries_provider,
            coverage_report_provider=self._coverage_report_provider,
            conversation_memory_service=self._conversation_memory_service,
            session_id=session_id,
            recent_queries=recent_queries,
            period=period,
            scenario=scenario,
        )
        return self._advisor_engine.build_agenda(advisor_input)

    def enrich_hybrid_result(
        self,
        result: HybridChatResult,
        *,
        session_id: str | None = None,
    ) -> HybridChatResult:
        advisor_input = build_advisor_input(
            dataset_summary_provider=self._dataset_summary_provider,
            top_queries_provider=self._top_queries_provider,
            coverage_report_provider=self._coverage_report_provider,
            conversation_memory_service=self._conversation_memory_service,
            session_id=session_id,
            hybrid_result=result,
        )
        return self._advisor_engine.enrich(advisor_input, result)
