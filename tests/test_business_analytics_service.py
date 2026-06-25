import pytest
from unittest.mock import MagicMock

from app.business_analytics.financial_service import FinancialAnalyticsService
from app.business_analytics.repository import BusinessAnalyticsRepository
from app.business_analytics.service import BusinessAnalyticsService


@pytest.fixture
def route_counts() -> dict[str, int]:
    return {
        "total_requests": 1000,
        "business_pipeline": 500,
        "slot_clarification": 100,
        "conversation_memory": 80,
        "capability_discovery": 70,
        "guided_fallback": 150,
        "legacy_chat": 100,
    }


@pytest.fixture
def repository(route_counts: dict[str, int]) -> MagicMock:
    repo = MagicMock(spec=BusinessAnalyticsRepository)
    repo.get_route_counts.return_value = route_counts
    repo.get_success_rate.return_value = 0.96
    repo.get_monthly_request_count.return_value = 800
    repo.get_performance_percentiles.return_value = {
        "p50_ms": 40.0,
        "p95_ms": 120.0,
        "p99_ms": 200.0,
        "avg_intent_ms": 5.0,
        "avg_planner_ms": 1.0,
        "avg_executor_ms": 8.0,
        "avg_response_ms": 0.5,
        "avg_total_ms": 25.0,
    }
    repo.get_top_queries_with_routes.return_value = [
        {
            "question": "¿Cuántos clientes existen?",
            "route": "business_pipeline",
            "count": 50,
            "success_rate": 1.0,
        }
    ]
    repo.get_top_routes.return_value = [
        {
            "handled_by": "business_pipeline",
            "query_type": "COUNT_CLIENTES",
            "count": 50,
            "success_rate": 1.0,
        }
    ]
    return repo


@pytest.fixture
def service(repository: MagicMock) -> BusinessAnalyticsService:
    return BusinessAnalyticsService(repository)


def test_get_coverage_returns_counts_and_percentages(service: BusinessAnalyticsService) -> None:
    coverage = service.get_coverage()

    assert coverage.total_requests == 1000
    assert coverage.business_pipeline == 500
    assert coverage.business_pipeline_pct == 50.0
    assert coverage.legacy_chat_pct == 10.0
    assert round(
        coverage.business_pipeline_pct
        + coverage.slot_clarification_pct
        + coverage.conversation_memory_pct
        + coverage.capability_discovery_pct
        + coverage.guided_fallback_pct
        + coverage.legacy_chat_pct,
        2,
    ) == 100.0


def test_get_performance_maps_percentiles(service: BusinessAnalyticsService) -> None:
    performance = service.get_performance()

    assert performance.p50_ms == 40.0
    assert performance.avg_intent_ms == 5.0
    assert performance.avg_total_ms == 25.0


def test_get_financial_calculates_avoidance_rate(service: BusinessAnalyticsService) -> None:
    financial = service.get_financial()

    assert financial.total_requests == 1000
    assert financial.deterministic_requests == 900
    assert financial.ai_requests == 100
    assert financial.ai_avoidance_rate == 0.9
    assert financial.legacy_dependency_rate == 0.1
    assert financial.estimated_gpt_equivalent_calls == 100
    assert financial.estimated_gpt_cost == 0.0


def test_get_top_queries_returns_route_and_success(service: BusinessAnalyticsService) -> None:
    items = service.get_top_queries(limit=5)

    assert len(items) == 1
    assert items[0].question == "¿Cuántos clientes existen?"
    assert items[0].route == "business_pipeline"
    assert items[0].success_rate == 1.0


def test_get_report_builds_coverage_score(service: BusinessAnalyticsService) -> None:
    report = service.get_report()

    assert report.deterministic_rate == 0.9
    assert report.legacy_rate == 0.1
    assert report.success_rate == 0.96
    assert report.coverage_score == 86.4
    assert len(report.top_routes) == 1


def test_validate_health_passes(service: BusinessAnalyticsService) -> None:
    result = service.validate_health()

    assert result["total_requests"] == 1000
    assert result["ai_avoidance_rate"] == 0.9


def test_financial_service_cost_with_settings(
    repository: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.core import settings as settings_module

    monkeypatch.setattr(settings_module.settings, "ESTIMATED_TOKENS_PER_LEGACY_CALL", 1000.0)
    monkeypatch.setattr(settings_module.settings, "GPT_COST_PER_1K_TOKENS", 0.01)

    financial = FinancialAnalyticsService(repository).get_financial_metrics()

    assert financial.estimated_gpt_cost == 1.0


def test_coverage_with_zero_requests(repository: MagicMock) -> None:
    repository.get_route_counts.return_value = {
        "total_requests": 0,
        "business_pipeline": 0,
        "slot_clarification": 0,
        "conversation_memory": 0,
        "capability_discovery": 0,
        "guided_fallback": 0,
        "legacy_chat": 0,
    }
    service = BusinessAnalyticsService(repository)
    coverage = service.get_coverage()

    assert coverage.total_requests == 0
    assert coverage.business_pipeline_pct == 0.0
