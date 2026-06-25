class EntityProfileHealthError(ValueError):
    """Invariante de salud del perfil empresarial violada."""


def validate_entity_profile_health(issues: dict[str, list[dict]]) -> dict:
    inconsistent_amounts = issues.get("inconsistent_amounts", [])
    invalid_dates = issues.get("invalid_dates", [])
    incomplete_distributions = issues.get("incomplete_distributions", [])
    profiles_without_movements = issues.get("profiles_without_movements", [])

    if inconsistent_amounts:
        raise EntityProfileHealthError(
            f"Existen {len(inconsistent_amounts)} perfiles con montos inconsistentes"
        )
    if invalid_dates:
        raise EntityProfileHealthError(
            f"Existen {len(invalid_dates)} perfiles con fechas inválidas"
        )
    if incomplete_distributions:
        raise EntityProfileHealthError(
            f"Existen {len(incomplete_distributions)} perfiles con distribución mensual incompleta"
        )

    return {
        "inconsistent_amounts_count": len(inconsistent_amounts),
        "invalid_dates_count": len(invalid_dates),
        "incomplete_distributions_count": len(incomplete_distributions),
        "profiles_without_movements_count": len(profiles_without_movements),
        "status": "healthy",
    }
