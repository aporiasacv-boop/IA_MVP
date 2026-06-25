import pytest

from app.semantic_intent.catalog_loader import load_enabled_verbs, load_objects, normalize_text
from app.semantic_intent.health import SemanticIntentHealthError, validate_semantic_health


def test_normalize_text() -> None:
    assert normalize_text("Análisis") == "analisis"


def test_load_catalogs() -> None:
    assert len(load_enabled_verbs()) >= 20
    assert len(load_objects()) >= 10


def test_health_ok() -> None:
    result = validate_semantic_health(
        {
            "unknown_verbs_count": 5,
            "ambiguous_objects": [],
            "incomplete_plans": [],
            "incompatible_strategies": [],
            "invalid_confidence": [],
        }
    )
    assert result["status"] == "healthy"


def test_health_ambiguous() -> None:
    with pytest.raises(SemanticIntentHealthError, match="ambiguos"):
        validate_semantic_health({"ambiguous_objects": [{"plan_id": "x"}]})
