from unittest.mock import MagicMock

from app.business_entity_master.metrics import BusinessEntityMasterMetrics
from app.business_entity_master.repository import BusinessEntityMasterRepository
from app.observability.metrics_repository import PerformanceMetricsRepository
from app.observability.metrics_service import MetricsService


def test_metrics_summary_includes_entity_fields() -> None:
    BusinessEntityMasterMetrics.reset_for_tests()
    BusinessEntityMasterMetrics.record_refresh(loaded=10, duplicated=2)

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

    bem_repo = MagicMock(spec=BusinessEntityMasterRepository)
    bem_repo.count_all.return_value = 2953

    service = MetricsService(perf_repo)
    original_repo_cls = BusinessEntityMasterRepository
    try:
        import app.observability.metrics_service as metrics_module

        metrics_module.BusinessEntityMasterRepository = lambda _session: bem_repo
        summary = service.get_summary()
    finally:
        metrics_module.BusinessEntityMasterRepository = original_repo_cls

    assert summary.business_entities_total == 2953
    assert summary.business_entities_loaded == 10
    assert summary.duplicated_entities == 2
