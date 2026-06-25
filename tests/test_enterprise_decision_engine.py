"""Pruebas del Enterprise Decision Engine v1."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.enterprise_decision.decision_engine import EnterpriseDecisionEngine, InsufficientEvidenceError
from app.enterprise_decision.evidence_analyzer import EvidenceAnalyzer
from app.enterprise_decision.health import build_decision_health
from app.enterprise_decision.metrics import get_enterprise_decision_metrics
from app.enterprise_decision.repository import DecisionContext, EnterpriseDecisionRepository
from app.enterprise_decision.schemas import DecisionRecommendRequest, DecisionType
from app.enterprise_decision.service import EnterpriseDecisionService
from app.main import app
from app.operational_metrics.repository import OperationalMetricsRepository
from app.operational_metrics.service import OperationalMetricsService
from app.schemas.hybrid_chat import HybridChatRequest, HybridChatResult


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
            request=HybridChatRequest(message="consulta de prueba", session_id="dec-1"),
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
            user_id="user-dec",
        )


def test_repository_gathers_sources() -> None:
    _seed_operational_data()
    context = EnterpriseDecisionRepository().gather(scenario_id="piloto")
    assert "operational_metrics" in context.sources_used
    assert "simulation_engine" in context.sources_used
    assert context.operational_queries == 5


def test_evidence_analyzer_produces_items() -> None:
    _seed_operational_data()
    context = EnterpriseDecisionRepository().gather(scenario_id="piloto")
    evidence = EvidenceAnalyzer().analyze(context)
    assert len(evidence) >= 4
    assert all(item.evidence_id for item in evidence)
    assert all(item.rule for item in evidence)


def test_decision_engine_builds_package_for_all_types() -> None:
    _seed_operational_data()
    context = EnterpriseDecisionRepository().gather(scenario_id="piloto")
    engine = EnterpriseDecisionEngine()
    for decision_type in DecisionType:
        package = engine.build_package(decision_type=decision_type, context=context)
        assert package.main_recommendation.evidence_ids
        assert package.evidence_used
        assert package.executive_summary
        assert package.confidence_level > 0
        assert "sql" not in package.executive_summary.lower()
        assert "prompt" not in package.executive_summary.lower()


def test_decision_engine_rejects_without_evidence() -> None:
    context = DecisionContext()
    engine = EnterpriseDecisionEngine()
    with pytest.raises(InsufficientEvidenceError):
        engine.build_package(decision_type=DecisionType.PROVEEDOR_IA, context=context)


def test_service_recommend_records_metrics() -> None:
    _seed_operational_data()
    service = EnterpriseDecisionService()
    package = service.recommend(
        DecisionRecommendRequest(decision_type=DecisionType.OPTIMIZACION_COSTOS),
    )
    stats = service.get_statistics()
    assert stats.decision_requests >= 1
    assert stats.recommendation_types.get("optimizacion_costos", 0) >= 1
    assert stats.average_confidence > 0
    assert package.financial_impact.avoided_cost_usd >= 0


def test_service_schema_and_health() -> None:
    _seed_operational_data()
    service = EnterpriseDecisionService()
    schema = service.get_schema()
    assert "proveedor_ia" in schema.decision_types
    assert len(schema.required_sections) >= 10
    health = service.health()
    assert health.status in {"healthy", "degraded"}
    assert "simulation_engine" in health.available_sources


def test_health_builds_missing_sources() -> None:
    health = build_decision_health(DecisionContext(sources_used=["finops"]))
    assert "simulation_engine" in health.missing_sources


def test_metrics_snapshot() -> None:
    metrics = get_enterprise_decision_metrics()
    metrics.record(
        decision_type="proveedor_ia",
        confidence=0.9,
        financial_impact=12.5,
        sources=["finops", "simulation_engine"],
    )
    snapshot = metrics.snapshot()
    assert snapshot["decision_requests"] >= 1
    assert snapshot["average_financial_impact"] > 0
    assert "finops" in snapshot["decision_sources"]


def test_api_decision_endpoints() -> None:
    _seed_operational_data()
    client = TestClient(app)
    schema = client.get("/api/decision/schema")
    assert schema.status_code == 200
    assert schema.json()["schema_id"] == "enterprise_decision_package_v1"

    example = client.get("/api/decision/example")
    assert example.status_code == 200
    body = example.json()
    assert body["main_recommendation"]["title"]
    assert len(body["evidence_used"]) > 0

    recommend = client.post(
        "/api/decision/recommend",
        json={"decision_type": "escenario", "scenario_id": "demo"},
    )
    assert recommend.status_code == 200
    assert recommend.json()["decision_type"] == "escenario"

    stats = client.get("/api/decision/statistics")
    assert stats.status_code == 200
    assert stats.json()["decision_requests"] >= 1


def test_api_recommend_returns_422_without_evidence() -> None:
    with patch.object(
        EnterpriseDecisionRepository,
        "gather",
        return_value=DecisionContext(),
    ):
        client = TestClient(app)
        response = client.post(
            "/api/decision/recommend",
            json={"decision_type": "proveedor_ia"},
        )
        assert response.status_code == 422


def test_repository_loads_eko_ero_eep_with_session() -> None:
    _seed_operational_data()
    session = MagicMock()
    with (
        patch("app.enterprise_knowledge.service.EnterpriseKnowledgeService") as eko_cls,
        patch("app.enterprise_reasoning.service.EnterpriseReasoningService") as ero_cls,
        patch("app.evidence_package.service.EvidencePackageService") as eep_cls,
    ):
        eko_cls.return_value.get_statistics.return_value = MagicMock(
            knowledge_objects_total=3,
            knowledge_average_completeness=0.85,
            knowledge_average_confidence=0.9,
        )
        ero_cls.return_value.get_statistics.return_value = MagicMock(
            reasoning_objects_total=2,
            average_reasoning_confidence=0.88,
        )
        eep_cls.return_value.get_statistics.return_value = MagicMock(
            evidence_packages_total=1,
            average_evidence_confidence=0.92,
        )
        context = EnterpriseDecisionRepository().gather(session=session, scenario_id="piloto")
    assert "eko" in context.sources_used
    assert "ero" in context.sources_used
    assert "eep" in context.sources_used
    assert context.eko_objects == 3


def test_metrics_summary_includes_decision_fields() -> None:
    _seed_operational_data()
    client = TestClient(app)
    client.post("/api/decision/recommend", json={"decision_type": "proveedor_ia"})
    summary = client.get("/api/metrics/summary")
    assert summary.status_code == 200
    data = summary.json()
    assert data["decision_requests"] >= 1
    assert "decision_sources" in data
