import pytest

from app.business_entity_profile.health import EntityProfileHealthError, validate_entity_profile_health


def test_health_passes_clean_state() -> None:
    result = validate_entity_profile_health(
        {
            "inconsistent_amounts": [],
            "invalid_dates": [],
            "incomplete_distributions": [],
            "profiles_without_movements": [{"profile_id": 1}],
            "entities_without_relations": [],
        }
    )
    assert result["status"] == "healthy"


def test_health_rejects_inconsistent_amounts() -> None:
    with pytest.raises(EntityProfileHealthError, match="montos inconsistentes"):
        validate_entity_profile_health(
            {
                "inconsistent_amounts": [{"profile_id": 1}],
                "invalid_dates": [],
                "incomplete_distributions": [],
                "profiles_without_movements": [],
                "entities_without_relations": [],
            }
        )


def test_health_rejects_invalid_dates() -> None:
    with pytest.raises(EntityProfileHealthError, match="fechas inválidas"):
        validate_entity_profile_health(
            {
                "inconsistent_amounts": [],
                "invalid_dates": [{"profile_id": 1}],
                "incomplete_distributions": [],
                "profiles_without_movements": [],
                "entities_without_relations": [],
            }
        )


def test_health_rejects_incomplete_distributions() -> None:
    with pytest.raises(EntityProfileHealthError, match="distribución mensual"):
        validate_entity_profile_health(
            {
                "inconsistent_amounts": [],
                "invalid_dates": [],
                "incomplete_distributions": [{"profile_id": 1}],
                "profiles_without_movements": [],
                "entities_without_relations": [],
            }
        )
