import pytest

from app.semantic_intent.metrics import SemanticIntentMetrics
from app.semantic_intent.schemas import SemanticParseRequest, SemanticPlanRequest
from app.semantic_intent.service import SemanticIntentService


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    SemanticIntentMetrics.reset_for_tests()


def test_service_get_verbs() -> None:
    service = SemanticIntentService()
    verbs = service.get_verbs()
    assert verbs.enabled_count >= 20


def test_service_parse_and_plan() -> None:
    service = SemanticIntentService()
    parse = service.parse(SemanticParseRequest(question="Listar clientes principales"))
    assert parse.business_verb is not None
    plan = service.plan(SemanticPlanRequest(question="Listar clientes principales"))
    assert plan.detected_verb == "listar"
    assert SemanticIntentMetrics.semantic_parses >= 2
    assert SemanticIntentMetrics.execution_plans >= 1


def test_service_statistics() -> None:
    service = SemanticIntentService()
    service.parse(SemanticParseRequest(question="Analizar movimientos del cliente"))
    stats = service.get_statistics()
    assert stats.semantic_parses >= 1


def test_service_validate_health() -> None:
    service = SemanticIntentService()
    assert service.validate_health()["status"] == "healthy"
