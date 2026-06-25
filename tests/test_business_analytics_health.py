import pytest
from unittest.mock import MagicMock

from app.business_analytics.service import BusinessAnalyticsService


def test_health_validation_rejects_inconsistent_percentages() -> None:
    repo = MagicMock()
    repo.get_route_counts.return_value = {
        "total_requests": 10,
        "business_pipeline": 10,
        "slot_clarification": 0,
        "conversation_memory": 0,
        "capability_discovery": 0,
        "guided_fallback": 0,
        "legacy_chat": 0,
    }
    repo.get_success_rate.return_value = 1.0
    repo.get_monthly_request_count.return_value = 10
    repo.get_performance_percentiles.return_value = {
        "p50_ms": 0,
        "p95_ms": 0,
        "p99_ms": 0,
        "avg_intent_ms": 0,
        "avg_planner_ms": 0,
        "avg_executor_ms": 0,
        "avg_response_ms": 0,
        "avg_total_ms": 0,
    }
    repo.get_top_routes.return_value = []

    service = BusinessAnalyticsService(repo)
    service.get_coverage = MagicMock(
        return_value=MagicMock(
            business_pipeline_pct=50.0,
            slot_clarification_pct=0.0,
            conversation_memory_pct=0.0,
            capability_discovery_pct=0.0,
            guided_fallback_pct=0.0,
            legacy_chat_pct=0.0,
        )
    )

    with pytest.raises(ValueError, match="Porcentajes inconsistentes"):
        service.validate_health()
