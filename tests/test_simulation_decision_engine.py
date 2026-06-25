"""Pruebas del Simulation & Decision Engine v1."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.operational_metrics.service import OperationalMetricsService
from app.operational_metrics.repository import OperationalMetricsRepository
from app.schemas.hybrid_chat import HybridChatRequest, HybridChatResult
from app.simulation_engine.decision_engine import DecisionEngine
from app.simulation_engine.forecast_engine import SimulationForecastEngine
from app.simulation_engine.metrics import get_simulation_engine_metrics
from app.simulation_engine.repository import SimulationBaselineRepository
from app.simulation_engine.scenario_engine import ScenarioEngine
from app.simulation_engine.schemas import SimulationScenarioInput
from app.simulation_engine.service import SimulationEngineService


def _seed_operational_data() -> None:
    service = OperationalMetricsService(OperationalMetricsRepository())
    for handled_by, tokens, latency in (
        ("business_pipeline", 0, 45.0),
        ("business_knowledge", 0, 35.0),
        ("conversation_memory", 0, 50.0),
        ("executive_reasoning", 1200, 900.0),
        ("legacy_chat", 800, 1200.0),
    ):
        service.record_query(
            request=HybridChatRequest(message="consulta de prueba", session_id="sim-1"),
            result=HybridChatResult(
                handled_by=handled_by,
                success=True,
                answer="respuesta de prueba suficientemente larga",
                metadata={
                    "tokens_input": tokens,
                    "tokens_output": tokens // 2,
                    "estimated_cost": 0.01 if handled_by == "executive_reasoning" else 0.0,
                    "provider": "openai" if handled_by == "executive_reasoning" else None,
                },
            ),
            wall_time_ms=latency,
            user_id="user-sim",
        )


def test_baseline_loads_from_operational_metrics() -> None:
    _seed_operational_data()
    baseline = SimulationBaselineRepository().load_baseline()
    assert baseline.source == "operational_metrics"
    assert baseline.total_historical_queries == 5
    assert baseline.route_mix.business_pipeline_pct > 0


def test_scenario_engine_lists_predefined() -> None:
    _seed_operational_data()
    baseline = SimulationBaselineRepository().load_baseline()
    scenarios = ScenarioEngine(baseline).list_predefined()
    assert len(scenarios) == 5
    assert scenarios[0].id == "demo"


def test_forecast_engine_simulates_and_compares_providers() -> None:
    _seed_operational_data()
    baseline = SimulationBaselineRepository().load_baseline()
    scenario = SimulationScenarioInput(scenario_id="piloto", name="Piloto", users=100)
    engine = ScenarioEngine(baseline)
    _, route_mix = engine.resolve(scenario)
    forecast = SimulationForecastEngine(baseline)
    metrics = forecast.simulate(scenario, route_mix)
    assert metrics.queries_per_month > 0
    assert metrics.avoided_cost_usd > 0
    providers = forecast.compare_providers(scenario, route_mix)
    assert len(providers) == 4
    assert min(providers, key=lambda p: p.cost_usd).provider in {"mock", "ollama"}


def test_decision_engine_recommendations() -> None:
    _seed_operational_data()
    service = SimulationEngineService()
    run = service.run(SimulationScenarioInput(scenario_id="demo", name="Demo"))
    recs = service.recommendations()
    assert len(recs.recommendations) >= 5
    assert any(item.title == "Proveedor más económico" for item in recs.recommendations)


def test_simulation_api_endpoints() -> None:
    _seed_operational_data()
    client = TestClient(app)
    scenarios = client.get("/api/simulation/scenarios")
    assert scenarios.status_code == 200
    assert len(scenarios.json()["predefined"]) == 5

    run = client.post(
        "/api/simulation/run",
        json={"scenario_id": "piloto", "name": "Piloto", "users": 100, "queries_per_user_day": 10},
    )
    assert run.status_code == 200
    assert run.json()["metrics"]["queries_per_month"] > 0

    comparison = client.get("/api/simulation/comparison")
    assert comparison.status_code == 200
    assert "cheapest_provider" in comparison.json()

    recommendations = client.get("/api/simulation/recommendations")
    assert recommendations.status_code == 200
    assert len(recommendations.json()["recommendations"]) >= 1

    assert get_simulation_engine_metrics().simulation_runs >= 1


def test_health_endpoint() -> None:
    service = SimulationEngineService()
    health = service.health()
    assert health.status == "ok"
