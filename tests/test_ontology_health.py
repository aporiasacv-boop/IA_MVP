import pytest

from app.business_ontology.health import OntologyHealthError, validate_ontology_health


def test_health_passes() -> None:
    result = validate_ontology_health(
        {
            "entities_without_suggestions": [{"canonical_id": 1}],
            "contradictory_rules": [],
            "incompatible_natures": [],
            "invalid_scores": [],
            "incomplete_relations": [],
        }
    )
    assert result["status"] == "healthy"


def test_health_rejects_contradictory() -> None:
    with pytest.raises(OntologyHealthError, match="contradictoria"):
        validate_ontology_health(
            {
                "entities_without_suggestions": [],
                "contradictory_rules": [{"canonical_id": 1}],
                "incompatible_natures": [],
                "invalid_scores": [],
                "incomplete_relations": [],
            }
        )


def test_health_rejects_invalid_scores() -> None:
    with pytest.raises(OntologyHealthError, match="score inválido"):
        validate_ontology_health(
            {
                "entities_without_suggestions": [],
                "contradictory_rules": [],
                "incompatible_natures": [],
                "invalid_scores": [{"assignment_id": 1}],
                "incomplete_relations": [],
            }
        )
