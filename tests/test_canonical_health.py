import pytest

from app.canonical_business_entity.health import (
    CanonicalEntityHealthError,
    validate_canonical_health,
)


def test_health_passes_clean_state() -> None:
    result = validate_canonical_health(
        {
            "orphan_entities": [],
            "duplicate_resolutions": [],
            "invalid_suggestion_scores": [],
            "invalid_resolution_scores": [],
        }
    )
    assert result["status"] == "healthy"


def test_health_rejects_orphans() -> None:
    with pytest.raises(CanonicalEntityHealthError, match="sin resolución"):
        validate_canonical_health(
            {
                "orphan_entities": [{"entity_id": 1}],
                "duplicate_resolutions": [],
                "invalid_suggestion_scores": [],
                "invalid_resolution_scores": [],
            }
        )


def test_health_rejects_duplicate_resolutions() -> None:
    with pytest.raises(CanonicalEntityHealthError, match="múltiples resoluciones"):
        validate_canonical_health(
            {
                "orphan_entities": [],
                "duplicate_resolutions": [{"entity_id": 1, "occurrences": 2}],
                "invalid_suggestion_scores": [],
                "invalid_resolution_scores": [],
            }
        )


def test_health_rejects_invalid_suggestion_scores() -> None:
    with pytest.raises(CanonicalEntityHealthError, match="score fuera de rango"):
        validate_canonical_health(
            {
                "orphan_entities": [],
                "duplicate_resolutions": [],
                "invalid_suggestion_scores": [{"suggestion_id": 1, "score": 1.5}],
                "invalid_resolution_scores": [],
            }
        )


def test_health_rejects_invalid_resolution_scores() -> None:
    with pytest.raises(CanonicalEntityHealthError, match="resoluciones con score"):
        validate_canonical_health(
            {
                "orphan_entities": [],
                "duplicate_resolutions": [],
                "invalid_suggestion_scores": [],
                "invalid_resolution_scores": [{"resolution_id": 1, "resolution_score": 2.0}],
            }
        )
