from app.business_analytics.constants import AI_ROUTE, DETERMINISTIC_ROUTES
from app.business_analytics.repository import BusinessAnalyticsRepository
from app.business_analytics.schemas import FinancialAnalyticsResponse
from app.core.settings import settings


def _safe_rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 4)


def _estimated_cost(requests: int, cost_per_1k_tokens: float) -> float:
    tokens = settings.ESTIMATED_TOKENS_PER_LEGACY_CALL
    if requests <= 0 or tokens <= 0 or cost_per_1k_tokens <= 0:
        return 0.0
    return round(requests * (tokens / 1000.0) * cost_per_1k_tokens, 4)


class FinancialAnalyticsService:
    def __init__(self, repository: BusinessAnalyticsRepository) -> None:
        self._repository = repository

    def get_financial_metrics(self) -> FinancialAnalyticsResponse:
        counts = self._repository.get_route_counts()
        total = counts["total_requests"]
        deterministic = sum(counts[route] for route in DETERMINISTIC_ROUTES)
        ai_requests = counts[AI_ROUTE]

        return FinancialAnalyticsResponse(
            total_requests=total,
            deterministic_requests=deterministic,
            ai_requests=ai_requests,
            ai_avoidance_rate=_safe_rate(deterministic, total),
            legacy_dependency_rate=_safe_rate(ai_requests, total),
            estimated_monthly_requests=self._repository.get_monthly_request_count(),
            estimated_gpt_equivalent_calls=ai_requests,
            estimated_claude_equivalent_calls=ai_requests,
            estimated_ollama_calls=ai_requests,
            estimated_gpt_cost=_estimated_cost(ai_requests, settings.GPT_COST_PER_1K_TOKENS),
            estimated_claude_cost=_estimated_cost(
                ai_requests,
                settings.CLAUDE_COST_PER_1K_TOKENS,
            ),
            estimated_ollama_cost=_estimated_cost(
                ai_requests,
                settings.OLLAMA_COST_PER_1K_TOKENS,
            ),
        )
