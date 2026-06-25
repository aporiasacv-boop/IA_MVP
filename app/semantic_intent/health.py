class SemanticIntentHealthError(ValueError):
    """Invariante de salud del planificador semántico violada."""


def validate_semantic_health(issues: dict[str, list | int | float]) -> dict:
    unknown_verbs = int(issues.get("unknown_verbs_count", 0))
    ambiguous_objects = issues.get("ambiguous_objects", [])
    incomplete_plans = issues.get("incomplete_plans", [])
    incompatible_strategies = issues.get("incompatible_strategies", [])
    invalid_confidence = issues.get("invalid_confidence", [])

    if unknown_verbs > 100:
        raise SemanticIntentHealthError(
            f"Demasiados verbos desconocidos acumulados: {unknown_verbs}"
        )
    if ambiguous_objects:
        raise SemanticIntentHealthError(
            f"Existen {len(ambiguous_objects)} planes con objetos ambiguos"
        )
    if incomplete_plans:
        raise SemanticIntentHealthError(
            f"Existen {len(incomplete_plans)} planes incompletos registrados"
        )
    if incompatible_strategies:
        raise SemanticIntentHealthError(
            f"Existen {len(incompatible_strategies)} estrategias incompatibles"
        )
    if invalid_confidence:
        raise SemanticIntentHealthError(
            f"Existen {len(invalid_confidence)} registros con confidence inválido"
        )

    return {
        "unknown_verbs_count": unknown_verbs,
        "ambiguous_objects_count": len(ambiguous_objects),
        "incomplete_plans_count": len(incomplete_plans),
        "incompatible_strategies_count": len(incompatible_strategies),
        "invalid_confidence_count": len(invalid_confidence),
        "status": "healthy",
    }
