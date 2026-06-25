class CanonicalEntityHealthError(ValueError):
    """Invariante de salud del catálogo canónico violada."""


def validate_canonical_health(issues: dict[str, list[dict]]) -> dict:
    orphans = issues.get("orphan_entities", [])
    duplicate_resolutions = issues.get("duplicate_resolutions", [])
    invalid_suggestion_scores = issues.get("invalid_suggestion_scores", [])
    invalid_resolution_scores = issues.get("invalid_resolution_scores", [])

    if orphans:
        raise CanonicalEntityHealthError(
            f"Existen {len(orphans)} entidades comerciales sin resolución canónica"
        )
    if duplicate_resolutions:
        raise CanonicalEntityHealthError(
            f"Existen {len(duplicate_resolutions)} entidades con múltiples resoluciones"
        )
    if invalid_suggestion_scores:
        raise CanonicalEntityHealthError(
            f"Existen {len(invalid_suggestion_scores)} sugerencias con score fuera de rango"
        )
    if invalid_resolution_scores:
        raise CanonicalEntityHealthError(
            f"Existen {len(invalid_resolution_scores)} resoluciones con score fuera de rango"
        )

    return {
        "orphan_entities_count": 0,
        "duplicate_resolutions_count": 0,
        "invalid_suggestion_scores_count": 0,
        "invalid_resolution_scores_count": 0,
        "status": "healthy",
    }
