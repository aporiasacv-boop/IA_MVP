from datetime import datetime

from app.enterprise_reasoning.metrics import EnterpriseReasoningMetrics


def test_metrics_snapshot() -> None:
    EnterpriseReasoningMetrics.reset_for_tests()
    EnterpriseReasoningMetrics.record_run(
        objects_total=50,
        rules_executed=500,
        average_confidence=0.82,
        average_findings=1.5,
        average_alerts=0.7,
        average_recommendations=1.1,
        build_time_seconds=3.2,
        run_at=datetime(2026, 6, 24),
    )
    snap = EnterpriseReasoningMetrics.snapshot()
    assert snap["reasoning_objects_total"] == 50
    assert snap["reasoning_rules_executed"] == 500
