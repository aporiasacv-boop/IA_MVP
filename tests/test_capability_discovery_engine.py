import pytest

from app.capability_discovery.detector import is_capability_discovery
from app.capability_discovery.engine import CapabilityDiscoveryEngine
from app.capability_discovery.health import (
    CapabilityDiscoveryHealthError,
    validate_capability_discovery_health,
)
from app.capability_discovery.v2.constants import (
    FORBIDDEN_EXAMPLE_PATTERNS,
    MAX_CAPABILITIES,
    MAX_EXAMPLES,
    MAX_RESPONSE_LINES,
    V2_CAPABILITIES,
    V2_EXAMPLES,
)
from app.capability_discovery.v2.formatter import build_v2_answer
from app.capability_discovery.v2.metrics import CapabilityDiscoveryV2Metrics
from app.capability_discovery.v2.validation import (
    CapabilityDiscoveryV2ValidationError,
    validate_v2_discovery_result,
)


@pytest.fixture(autouse=True)
def reset_v2_metrics() -> None:
    CapabilityDiscoveryV2Metrics.reset()


@pytest.fixture
def engine() -> CapabilityDiscoveryEngine:
    return CapabilityDiscoveryEngine()


@pytest.mark.parametrize(
    "question",
    [
        "¿Qué puedes hacer?",
        "¿Qué consultas soportas?",
        "¿Cómo puedes ayudarme?",
        "¿Para qué sirves?",
    ],
)
def test_is_capability_discovery_detects_discovery_questions(question: str) -> None:
    assert is_capability_discovery(question) is True


def test_is_capability_discovery_dataset_questions_go_to_business_pipeline() -> None:
    assert is_capability_discovery("¿Qué datos tienes?") is False
    assert is_capability_discovery("¿Qué información tienes?") is False


def test_discover_v2_limits_capabilities_and_examples(engine: CapabilityDiscoveryEngine) -> None:
    result = engine.discover()

    assert result.success is True
    assert len(result.capabilities) == MAX_CAPABILITIES
    assert len(result.example_questions) == MAX_EXAMPLES
    assert result.capabilities == list(V2_CAPABILITIES)
    assert result.example_questions == list(V2_EXAMPLES)


def test_discover_v2_answer_is_conversational(engine: CapabilityDiscoveryEngine) -> None:
    result = engine.discover()

    assert result.answer.startswith("Puedo ayudarte con información sobre:")
    assert "Por ejemplo:" in result.answer
    assert len(result.answer.splitlines()) <= MAX_RESPONSE_LINES
    assert "Cobertura de datos" not in result.answer
    assert "Consultas empresariales soportadas" not in result.answer
    assert "Rankings" not in result.answer
    assert "Cuentas" not in result.answer


def test_discover_v2_has_no_suggestions(engine: CapabilityDiscoveryEngine) -> None:
    result = engine.discover()
    assert result.suggestions is None


def test_discover_v2_forbidden_examples_not_in_response(engine: CapabilityDiscoveryEngine) -> None:
    result = engine.discover()
    normalized = result.answer.lower()
    for pattern in FORBIDDEN_EXAMPLE_PATTERNS:
        assert pattern not in normalized


def test_discover_v2_records_metrics(engine: CapabilityDiscoveryEngine) -> None:
    engine.discover()
    snapshot = CapabilityDiscoveryV2Metrics.snapshot()
    assert snapshot["capability_discovery_v2_responses"] == 1
    assert snapshot["capability_discovery_response_length"] <= MAX_RESPONSE_LINES


def test_build_v2_answer_matches_template() -> None:
    answer = build_v2_answer(V2_CAPABILITIES, V2_EXAMPLES)
    assert "• Clientes" in answer
    assert "• ¿Cuántos clientes existen?" in answer
    assert len(answer.splitlines()) == 12


def test_validate_v2_rejects_too_many_capabilities() -> None:
    with pytest.raises(CapabilityDiscoveryV2ValidationError, match="Máximo 5 capacidades"):
        validate_v2_discovery_result(
            answer="x",
            capabilities=["a"] * 6,
            example_questions=list(V2_EXAMPLES),
            suggestions_present=False,
        )


def test_validate_v2_rejects_suggestions() -> None:
    with pytest.raises(CapabilityDiscoveryV2ValidationError, match="suggested_questions"):
        validate_v2_discovery_result(
            answer=build_v2_answer(V2_CAPABILITIES, V2_EXAMPLES),
            capabilities=list(V2_CAPABILITIES),
            example_questions=list(V2_EXAMPLES),
            suggestions_present=True,
        )


def test_health_validation_passes_with_v2_engine() -> None:
    report = validate_capability_discovery_health()
    assert report["discovery_version"] == "v2"
    assert report["capabilities_count"] == 5
    assert report["example_questions_count"] == 3


def test_health_validation_requires_capabilities() -> None:
    class BrokenEngine(CapabilityDiscoveryEngine):
        def discover(self):
            result = super().discover()
            return result.model_copy(update={"capabilities": []})

    with pytest.raises(CapabilityDiscoveryHealthError):
        validate_capability_discovery_health(BrokenEngine())
