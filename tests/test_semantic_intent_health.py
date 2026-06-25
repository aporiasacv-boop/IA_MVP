import pytest

from app.semantic_intent.health import SemanticIntentHealthError, validate_semantic_health


def test_health_incomplete_plans() -> None:
    with pytest.raises(SemanticIntentHealthError, match="incompletos"):
        validate_semantic_health({"incomplete_plans": [{"plan_id": "x"}]})


def test_health_incompatible() -> None:
    with pytest.raises(SemanticIntentHealthError, match="incompatibles"):
        validate_semantic_health({"incompatible_strategies": [{"plan_id": "x"}]})


def test_health_invalid_confidence() -> None:
    with pytest.raises(SemanticIntentHealthError, match="confidence"):
        validate_semantic_health({"invalid_confidence": [{"plan_id": "x"}]})


def test_health_too_many_unknown_verbs() -> None:
    with pytest.raises(SemanticIntentHealthError, match="desconocidos"):
        validate_semantic_health({"unknown_verbs_count": 150})
