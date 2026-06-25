class BusinessEntityMasterHealthError(ValueError):
    """Invariante de salud del catálogo maestro violada."""


def validate_entity_master_health(issues: dict[str, list[dict]]) -> dict:
    empty_names = issues.get("empty_names", [])
    inconsistent_dates = issues.get("inconsistent_dates", [])
    inconsistent_amounts = issues.get("inconsistent_amounts", [])

    if empty_names:
        raise BusinessEntityMasterHealthError(
            f"Existen {len(empty_names)} entidades con nombre vacío"
        )
    if inconsistent_dates:
        raise BusinessEntityMasterHealthError(
            f"Existen {len(inconsistent_dates)} entidades con fechas inconsistentes"
        )
    if inconsistent_amounts:
        raise BusinessEntityMasterHealthError(
            f"Existen {len(inconsistent_amounts)} entidades con montos inconsistentes"
        )

    duplicated = issues.get("duplicated_codes", [])
    return {
        "duplicated_codes_count": len(duplicated),
        "empty_names_count": 0,
        "inconsistent_dates_count": 0,
        "inconsistent_amounts_count": 0,
        "status": "healthy",
    }
