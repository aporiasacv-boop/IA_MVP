import pytest

from app.capability_discovery.health import (
    CapabilityDiscoveryHealthError,
    validate_capability_discovery_health,
)
from app.capability_discovery.engine import CapabilityDiscoveryEngine
from app.query_engine.query_planner import BusinessQueryPlanner
from app.services.semantic_intent_builder import SemanticIntentBuilder


def test_health_validation_passes_with_default_engine() -> None:
    report = validate_capability_discovery_health()

    assert report["capabilities_count"] == 5
    assert report["example_questions_count"] == 3
    assert report["discovery_version"] == "v2"


def test_health_validation_requires_capabilities() -> None:
    class BrokenEngine(CapabilityDiscoveryEngine):
        def discover(self):
            result = super().discover()
            return result.model_copy(update={"capabilities": []})

    with pytest.raises(CapabilityDiscoveryHealthError, match="Capacidades"):
        validate_capability_discovery_health(BrokenEngine())


def test_health_validation_requires_example_questions() -> None:
    class BrokenEngine(CapabilityDiscoveryEngine):
        def discover(self):
            result = super().discover()
            return result.model_copy(update={"example_questions": []})

    with pytest.raises(CapabilityDiscoveryHealthError):
        validate_capability_discovery_health(BrokenEngine())


def test_example_questions_do_not_raise_when_routed_through_planner() -> None:
    engine = CapabilityDiscoveryEngine()
    planner = BusinessQueryPlanner()
    intent_builder = SemanticIntentBuilder()
    discovery = engine.discover()

    for question in discovery.example_questions:
        intent = intent_builder.build(question)
        query = planner.plan(intent)
        assert query.query_type.value != "UNSUPPORTED", question
