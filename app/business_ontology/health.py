class OntologyHealthError(ValueError):
    """Invariante de salud de la ontología violada."""


def validate_ontology_health(issues: dict[str, list[dict]]) -> dict:
    contradictory_rules = issues.get("contradictory_rules", [])
    incompatible_natures = issues.get("incompatible_natures", [])
    invalid_scores = issues.get("invalid_scores", [])
    incomplete_relations = issues.get("incomplete_relations", [])

    if contradictory_rules:
        raise OntologyHealthError(
            f"Existen {len(contradictory_rules)} entidades con reglas contradictorias"
        )
    if incompatible_natures:
        raise OntologyHealthError(
            f"Existen {len(incompatible_natures)} entidades con naturalezas incompatibles"
        )
    if invalid_scores:
        raise OntologyHealthError(
            f"Existen {len(invalid_scores)} asignaciones con score inválido"
        )
    if incomplete_relations:
        raise OntologyHealthError(
            f"Existen {len(incomplete_relations)} asignaciones con relaciones incompletas"
        )

    return {
        "entities_without_suggestions_count": len(issues.get("entities_without_suggestions", [])),
        "contradictory_rules_count": len(contradictory_rules),
        "incompatible_natures_count": len(incompatible_natures),
        "invalid_scores_count": len(invalid_scores),
        "incomplete_relations_count": len(incomplete_relations),
        "status": "healthy",
    }
