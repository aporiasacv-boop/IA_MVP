"""Pruebas de Operational Metrics & FinOps v2."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.operational_metrics.collector import build_operational_record
from app.operational_metrics.cost_engine import (
    avoided_llm_cost_usd,
    benchmark_cost_usd,
    is_llm_route,
    provider_token_cost_usd,
)
from app.operational_metrics.forecast_engine import ForecastEngine
from app.operational_metrics.metrics import get_operational_finops_metrics, reset_operational_finops_metrics
from app.operational_metrics.repository import OperationalMetricsRepository, reset_operational_memory_store
from app.operational_metrics.service import OperationalMetricsService
from app.operational_metrics.aggregator import OperationalMetricsAggregator
from app.schemas.hybrid_chat import HybridChatRequest, HybridChatResult


@pytest.fixture(autouse=True)
def reset_state() -> None:
    reset_operational_memory_store()
    reset_operational_finops_metrics()


def _record(handled_by: str, **metadata) -> None:
    service = OperationalMetricsService(OperationalMetricsRepository())
    service.record_query(
        request=HybridChatRequest(message="¿Cuántos clientes hay?", session_id="sess-1"),
        result=HybridChatResult(
            handled_by=handled_by,
            success=True,
            answer="Respuesta de prueba con contenido suficiente.",
            metadata={"query_type": "TEST", "confidence": 1.0, **metadata},
        ),
        wall_time_ms=120.0,
        user_id="user-1",
    )


def test_cost_engine_llm_detection_and_benchmark() -> None:
    assert is_llm_route("legacy_chat") is True
    assert is_llm_route("business_pipeline") is False
    assert provider_token_cost_usd("openai", 1000, 500) > 0
    assert avoided_llm_cost_usd() > 0
    assert benchmark_cost_usd("claude", 800, 400) >= 0


def test_collector_executive_reasoning_real_tokens() -> None:
    record = build_operational_record(
        request=HybridChatRequest(message="Analiza el negocio"),
        result=HybridChatResult(
            handled_by="executive_reasoning",
            success=True,
            answer="Análisis ejecutivo",
            metadata={
                "provider": "openai",
                "model": "gpt-4o-mini",
                "tokens_input": 1200,
                "tokens_output": 600,
                "estimated_cost": 0.012,
                "confidence": 0.9,
            },
        ),
        wall_time_ms=900.0,
    )
    assert record.token_source == "api"
    assert record.llm_used is True
    assert record.cost_usd == 0.012
    assert record.cost_mxn > 0


def test_collector_pipeline_avoids_llm_cost() -> None:
    record = build_operational_record(
        request=HybridChatRequest(message="¿Cuántos clientes?"),
        result=HybridChatResult(
            handled_by="business_pipeline",
            success=True,
            answer="50 clientes",
            metadata={"query_type": "COUNT_CLIENTES", "confidence": 1.0},
        ),
        wall_time_ms=40.0,
    )
    assert record.pipeline_hit is True
    assert record.llm_used is False
    assert record.avoided_cost_usd > 0


def test_service_aggregator_and_forecast() -> None:
    _record("business_pipeline")
    _record("business_knowledge")
    _record(
        "executive_reasoning",
        provider="openai",
        model="gpt-4o-mini",
        tokens_input=1000,
        tokens_output=400,
        estimated_cost=0.01,
    )
    service = OperationalMetricsService(OperationalMetricsRepository())
    overview = service.overview()
    assert overview.total_queries == 3
    assert overview.llm_avoidance_rate > 0
    savings = service.savings()
    assert savings.total_avoided_cost_usd > 0
    providers = service.providers()
    assert any(item.provider == "openai" for item in providers.providers)
    forecast = service.forecast()
    assert len(forecast.scenarios) == 5
    assert forecast.scenarios[0].users == 100


def test_collector_legacy_chat_estimated_tokens() -> None:
    record = build_operational_record(
        request=HybridChatRequest(message="Hola, ¿cómo estás?"),
        result=HybridChatResult(
            handled_by="legacy_chat",
            success=True,
            answer="Estoy operativo para ayudarte con consultas empresariales.",
            metadata={"intent": "greeting", "confidence": 0.9},
        ),
        wall_time_ms=500.0,
    )
    assert record.llm_used is True
    assert record.token_source == "estimated"
    assert record.total_tokens > 0


def test_health_endpoint() -> None:
    service = OperationalMetricsService(OperationalMetricsRepository())
    health = service.health()
    assert health.status in {"ok", "degraded"}


def test_finops_api_endpoints() -> None:
    _record("guided_fallback", fallback_type="AMBIGUOUS")
    client = TestClient(app)
    overview = client.get("/api/finops/overview")
    assert overview.status_code == 200
    assert overview.json()["total_queries"] >= 1

    costs = client.get("/api/finops/costs")
    assert costs.status_code == 200
    assert "by_handled_by" in costs.json()

    providers = client.get("/api/finops/providers")
    assert providers.status_code == 200

    forecast = client.get("/api/finops/forecast")
    assert forecast.status_code == 200
    assert len(forecast.json()["scenarios"]) == 5

    savings = client.get("/api/finops/savings")
    assert savings.status_code == 200

    trends = client.get("/api/finops/trends")
    assert trends.status_code == 200


def test_hybrid_chat_records_operational_metric() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/chat/hybrid",
        json={"message": "¿Qué es un cliente?", "session_id": "finops-test"},
    )
    assert response.status_code == 200
    overview = OperationalMetricsAggregator(
        OperationalMetricsRepository().list_records()
    ).overview()
    assert overview.total_queries >= 1
