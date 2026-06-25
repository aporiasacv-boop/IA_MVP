from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.observability.db_timing import track_database_call
from app.observability.metrics_repository import PerformanceMetricsRepository
from app.observability.metrics_service import MetricsService
from app.observability.performance_metrics import (
    PerformanceCollector,
    PerformanceMetrics,
    add_database_time,
    get_database_time,
    reset_database_time,
    set_active_collector,
)
from app.observability.performance_tracker import PerformanceTracker
from app.schemas.metrics import MetricsSummaryResponse


@pytest.fixture
def mock_session() -> MagicMock:
    session = MagicMock()
    session.execute.return_value.mappings.return_value.one.return_value = {
        "total_requests": 1000,
        "business_pipeline_requests": 720,
        "legacy_chat_requests": 280,
        "guided_fallback_requests": 45,
        "capability_discovery_requests": 35,
        "slot_clarification_requests": 30,
        "conversation_memory_requests": 25,
        "suggested_questions_generated": 420,
        "average_suggestions_per_response": 3.8,
        "avg_total_time_ms": 85.3,
        "avg_database_time_ms": 22.1,
        "avg_ollama_time_ms": 1800.0,
    }
    session.execute.return_value.mappings.return_value.all.return_value = [
        {"question": "¿Cuántos clientes existen?", "count": 124},
    ]
    return session


@pytest.fixture
def repository(mock_session: MagicMock) -> PerformanceMetricsRepository:
    return PerformanceMetricsRepository(mock_session)


def test_performance_collector_finalize() -> None:
    collector = PerformanceCollector(question="¿Cuántos clientes existen?")
    collector.record_stage("intent", 10.5)
    collector.record_stage("planner", 2.0)

    metrics = collector.finalize(
        handled_by="business_pipeline",
        success=True,
        query_type="COUNT_CLIENTES",
        database_time_ms=5.5,
    )

    assert metrics.question == "¿Cuántos clientes existen?"
    assert metrics.intent_time_ms == 10.5
    assert metrics.planner_time_ms == 2.0
    assert metrics.database_time_ms == 5.5
    assert metrics.handled_by == "business_pipeline"
    assert metrics.success is True
    assert metrics.total_time_ms >= 0


def test_performance_tracker_persists_metrics(mock_session: MagicMock) -> None:
    tracker = PerformanceTracker(mock_session)
    collector = tracker.start_request("¿Cuántos clientes existen?")
    tracker.record_stage(collector, "intent", 12.0)
    metrics = tracker.finish_request(
        collector,
        handled_by="business_pipeline",
        success=True,
        query_type="COUNT_CLIENTES",
    )
    tracker.persist(metrics)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    saved = mock_session.add.call_args.args[0]
    assert saved.question == "¿Cuántos clientes existen?"
    assert saved.handled_by == "business_pipeline"


def test_track_database_call_accumulates_time() -> None:
    reset_database_time()
    set_active_collector(PerformanceCollector(question="test"))

    def slow_operation() -> str:
        return "ok"

    result = track_database_call(slow_operation)

    assert result == "ok"
    assert get_database_time() >= 0


def test_metrics_repository_save(repository: PerformanceMetricsRepository, mock_session: MagicMock) -> None:
    metrics = PerformanceMetrics(
        request_id="req-1",
        question="¿Cuántos clientes existen?",
        handled_by="business_pipeline",
        intent_time_ms=10.0,
        total_time_ms=20.0,
        query_type="COUNT_CLIENTES",
        success=True,
        created_at=datetime.now(timezone.utc),
    )

    repository.save(metrics)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


def test_metrics_repository_get_summary(repository: PerformanceMetricsRepository) -> None:
    summary = repository.get_summary()

    assert summary["total_requests"] == 1000
    assert summary["business_pipeline_requests"] == 720
    assert summary["legacy_chat_requests"] == 280
    assert summary["guided_fallback_requests"] == 45
    assert summary["capability_discovery_requests"] == 35
    assert summary["suggested_questions_generated"] == 420
    assert summary["average_suggestions_per_response"] == 3.8
    assert summary["avg_total_time_ms"] == 85.3


def test_metrics_repository_get_routing_metrics(
    repository: PerformanceMetricsRepository,
    mock_session: MagicMock,
) -> None:
    mock_session.execute.return_value.mappings.return_value.all.side_effect = [
        [
            {
                "handled_by": "business_pipeline",
                "count": 720,
                "success_rate": 0.98,
            },
            {
                "handled_by": "guided_fallback",
                "count": 45,
                "success_rate": 1.0,
            },
        ],
        [
            {
                "handled_by": "guided_fallback",
                "query_type": "UNKNOWN",
                "count": 30,
            },
        ],
    ]

    routing = repository.get_routing_metrics(path_limit=5)

    assert routing["handled_by_distribution"][0]["handled_by"] == "business_pipeline"
    assert routing["success_rate_by_handled_by"]["guided_fallback"] == 1.0
    assert routing["top_paths"][0]["query_type"] == "UNKNOWN"


def test_metrics_repository_get_top_queries(repository: PerformanceMetricsRepository) -> None:
    top_queries = repository.get_top_queries(limit=5)

    assert top_queries == [{"question": "¿Cuántos clientes existen?", "count": 124}]


def test_metrics_repository_get_performance(repository: PerformanceMetricsRepository, mock_session: MagicMock) -> None:
    mock_session.execute.return_value.mappings.return_value.one.side_effect = [
        {
            "p50_total_time_ms": 50.0,
            "p95_total_time_ms": 120.0,
            "p99_total_time_ms": 200.0,
        },
        {
            "operation_time_ms": 1.0,
            "entity_time_ms": 2.0,
            "intent_time_ms": 10.0,
            "planner_time_ms": 1.5,
            "executor_time_ms": 8.0,
            "database_time_ms": 5.0,
            "response_time_ms": 0.5,
            "legacy_chat_time_ms": None,
            "ollama_time_ms": None,
            "total_time_ms": 25.0,
        },
    ]

    performance = repository.get_performance()

    assert performance["p50_total_time_ms"] == 50.0
    assert performance["p95_total_time_ms"] == 120.0
    assert performance["averages"]["intent_time_ms"] == 10.0


def test_metrics_service_get_summary(repository: PerformanceMetricsRepository) -> None:
    service = MetricsService(repository)
    summary = service.get_summary()

    assert isinstance(summary, MetricsSummaryResponse)
    assert summary.total_requests == 1000


@pytest.fixture
def metrics_client(mock_session: MagicMock) -> TestClient:
    service = MetricsService(PerformanceMetricsRepository(mock_session))

    def override_metrics_service():
        return service

    from app.api.deps import get_metrics_service

    app.dependency_overrides[get_metrics_service] = override_metrics_service
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_metrics_summary_endpoint(metrics_client: TestClient) -> None:
    response = metrics_client.get("/api/metrics/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_requests"] == 1000
    assert data["avg_database_time_ms"] == 22.1


def test_metrics_top_queries_endpoint(metrics_client: TestClient) -> None:
    response = metrics_client.get("/api/metrics/top-queries")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["question"] == "¿Cuántos clientes existen?"
    assert data[0]["count"] == 124


def test_metrics_routing_endpoint(metrics_client: TestClient, mock_session: MagicMock) -> None:
    mock_session.execute.return_value.mappings.return_value.all.side_effect = [
        [
            {
                "handled_by": "guided_fallback",
                "count": 10,
                "success_rate": 1.0,
            }
        ],
        [
            {
                "handled_by": "guided_fallback",
                "query_type": "UNKNOWN",
                "count": 10,
            }
        ],
    ]

    response = metrics_client.get("/api/metrics/routing")
    assert response.status_code == 200
    data = response.json()
    assert data["handled_by_distribution"][0]["handled_by"] == "guided_fallback"
    assert data["top_paths"][0]["query_type"] == "UNKNOWN"


def test_metrics_performance_endpoint(metrics_client: TestClient, mock_session: MagicMock) -> None:
    mock_session.execute.return_value.mappings.return_value.one.side_effect = [
        {
            "p50_total_time_ms": 40.0,
            "p95_total_time_ms": 90.0,
            "p99_total_time_ms": 150.0,
        },
        {
            "operation_time_ms": 1.0,
            "entity_time_ms": 1.0,
            "intent_time_ms": 5.0,
            "planner_time_ms": 1.0,
            "executor_time_ms": 4.0,
            "database_time_ms": 3.0,
            "response_time_ms": 0.5,
            "legacy_chat_time_ms": None,
            "ollama_time_ms": None,
            "total_time_ms": 15.0,
        },
    ]

    response = metrics_client.get("/api/metrics/performance")
    assert response.status_code == 200
    data = response.json()
    assert data["p50_total_time_ms"] == 40.0
    assert data["averages"]["executor_time_ms"] == 4.0
