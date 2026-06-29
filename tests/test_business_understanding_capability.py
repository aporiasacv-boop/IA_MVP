import pytest

from app.capabilities.business_understanding_capability import BusinessUnderstandingCapability
from app.query_engine.query_types import BusinessQueryType
from app.query_engine.query_planner import BusinessQueryPlanner
from app.services.semantic_intent_builder import SemanticIntentBuilder


@pytest.fixture
def capability() -> BusinessUnderstandingCapability:
    return BusinessUnderstandingCapability(
        SemanticIntentBuilder(),
        BusinessQueryPlanner(),
    )


def test_understand_count_clientes(capability: BusinessUnderstandingCapability) -> None:
    stage = capability.understand("¿Cuántos clientes existen?")

    assert stage.result.query.query_type == BusinessQueryType.COUNT_CLIENTES
    assert stage.result.intent.confidence > 0
    assert stage.intent_stage_ms >= 0
    assert stage.planner_stage_ms >= 0


def test_understand_unsupported_question(capability: BusinessUnderstandingCapability) -> None:
    stage = capability.understand("¿Qué es un proveedor?")

    assert stage.result.query.query_type == BusinessQueryType.UNSUPPORTED


def test_understand_produces_intent_and_query_together(
    capability: BusinessUnderstandingCapability,
) -> None:
    stage = capability.understand("Muéstrame los principales clientes")

    assert stage.result.intent.source_question == "Muéstrame los principales clientes"
    assert stage.result.query.query_type == BusinessQueryType.TOP_CLIENTES
