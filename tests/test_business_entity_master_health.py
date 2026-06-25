import pytest

from app.business_entity_master.health import (
    BusinessEntityMasterHealthError,
    validate_entity_master_health,
)


def test_health_passes_with_duplicated_codes_only() -> None:
    result = validate_entity_master_health(
        {
            "duplicated_codes": [{"entity_code": "20401001", "occurrences": 2}],
            "empty_names": [],
            "inconsistent_dates": [],
            "inconsistent_amounts": [],
        }
    )
    assert result["status"] == "healthy"
    assert result["duplicated_codes_count"] == 1


def test_health_rejects_empty_names() -> None:
    with pytest.raises(BusinessEntityMasterHealthError, match="nombre vacío"):
        validate_entity_master_health(
            {
                "duplicated_codes": [],
                "empty_names": [{"entity_id": 1, "entity_code": "X", "source_column": "a"}],
                "inconsistent_dates": [],
                "inconsistent_amounts": [],
            }
        )


def test_health_rejects_inconsistent_dates() -> None:
    with pytest.raises(BusinessEntityMasterHealthError, match="fechas inconsistentes"):
        validate_entity_master_health(
            {
                "duplicated_codes": [],
                "empty_names": [],
                "inconsistent_dates": [
                    {
                        "entity_id": 1,
                        "entity_code": "X",
                        "first_seen": "2025-12-31",
                        "last_seen": "2025-01-01",
                    }
                ],
                "inconsistent_amounts": [],
            }
        )


def test_health_rejects_negative_amounts() -> None:
    with pytest.raises(BusinessEntityMasterHealthError, match="montos inconsistentes"):
        validate_entity_master_health(
            {
                "duplicated_codes": [],
                "empty_names": [],
                "inconsistent_dates": [],
                "inconsistent_amounts": [
                    {
                        "entity_id": 1,
                        "entity_code": "X",
                        "movement_count": -1,
                        "movement_amount": 10,
                    }
                ],
            }
        )
