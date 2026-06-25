from datetime import datetime

from app.enterprise_knowledge.metrics import EnterpriseKnowledgeMetrics


def test_metrics_snapshot() -> None:
    EnterpriseKnowledgeMetrics.reset_for_tests()
    run_at = datetime(2026, 6, 24)
    EnterpriseKnowledgeMetrics.record_run(
        objects_total=100,
        build_time_seconds=5.5,
        average_completeness=0.82,
        average_confidence=0.78,
        run_at=run_at,
    )
    snap = EnterpriseKnowledgeMetrics.snapshot()
    assert snap["knowledge_objects_total"] == 100
    assert snap["knowledge_build_time"] == 5.5
