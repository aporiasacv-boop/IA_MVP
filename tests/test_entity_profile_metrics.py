from datetime import datetime

from app.business_entity_profile.metrics import EntityProfileMetrics


def test_metrics_record_and_snapshot() -> None:
    EntityProfileMetrics.reset_for_tests()
    run_at = datetime(2026, 6, 24, 10, 0, 0)
    EntityProfileMetrics.record_run(
        profiles_total=50,
        average_completeness=0.82,
        generation_time_seconds=3.5,
        run_at=run_at,
    )
    snapshot = EntityProfileMetrics.snapshot()
    assert snapshot["entity_profiles_total"] == 50
    assert snapshot["average_profile_completeness"] == 0.82
    assert snapshot["profile_generation_time"] == 3.5
    assert snapshot["last_profile_refresh"] == run_at
