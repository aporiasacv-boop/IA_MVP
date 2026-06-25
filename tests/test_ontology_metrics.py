from datetime import datetime

from app.business_ontology.metrics import BusinessOntologyMetrics


def test_metrics_snapshot() -> None:
    BusinessOntologyMetrics.reset_for_tests()
    run_at = datetime(2026, 6, 24)
    BusinessOntologyMetrics.record_run(
        entities=100,
        pending=80,
        approved=10,
        rules=25,
        average_confidence=0.82,
        run_at=run_at,
    )
    snap = BusinessOntologyMetrics.snapshot()
    assert snap["ontology_entities"] == 100
    assert snap["ontology_pending"] == 80
    assert snap["ontology_average_confidence"] == 0.82
