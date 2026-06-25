from unittest.mock import MagicMock

from app.canonical_business_entity.metrics import CanonicalEntityMetrics
from app.canonical_business_entity.repository import CanonicalBusinessEntityRepository
from app.observability.metrics_repository import PerformanceMetricsRepository
from app.observability.metrics_service import MetricsService


def test_metrics_summary_includes_canonical_fields() -> None:
    CanonicalEntityMetrics.reset_for_tests()
    CanonicalEntityMetrics.record_run(
        canonical_total=50,
        canonical_matches=3,
        pending_matches=8,
        automatic_suggestions=20,
    )
    perf_repo = MagicMock(spec=PerformanceMetricsRepository)
    perf_repo.get_summary.return_value = {
        "total_requests": 0,
        "business_pipeline_requests": 0,
        "legacy_chat_requests": 0,
        "guided_fallback_requests": 0,
        "capability_discovery_requests": 0,
        "slot_clarification_requests": 0,
        "conversation_memory_requests": 0,
        "suggested_questions_generated": 0,
        "average_suggestions_per_response": 0.0,
        "avg_total_time_ms": 0.0,
        "avg_database_time_ms": None,
        "avg_ollama_time_ms": None,
    }
    perf_repo.session = MagicMock()

    import app.observability.metrics_service as metrics_module

    bem_repo = MagicMock()
    bem_repo.count_all.return_value = 100
    cbe_repo = MagicMock(spec=CanonicalBusinessEntityRepository)
    cbe_repo.count_canonical.return_value = 50
    cbe_repo.count_canonical_matches.return_value = 3
    cbe_repo.count_pending_suggestions.return_value = 8
    cbe_repo.count_automatic_suggestions.return_value = 20

    original_bem = metrics_module.BusinessEntityMasterRepository
    original_cbe = metrics_module.CanonicalBusinessEntityRepository
    try:
        metrics_module.BusinessEntityMasterRepository = lambda _s: bem_repo
        metrics_module.CanonicalBusinessEntityRepository = lambda _s: cbe_repo
        summary = MetricsService(perf_repo).get_summary()
    finally:
        metrics_module.BusinessEntityMasterRepository = original_bem
        metrics_module.CanonicalBusinessEntityRepository = original_cbe

    assert summary.canonical_entities_total == 50
    assert summary.pending_matches == 8
