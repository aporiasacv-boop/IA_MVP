class ReasoningHealthError(ValueError):
    """Invariante de salud del razonamiento empresarial violada."""


def validate_reasoning_health(issues: dict[str, list[dict]]) -> dict:
    missing_evidence = issues.get("missing_evidence", [])
    invalid_confidence = issues.get("invalid_confidence", [])
    duplicate_findings = issues.get("duplicate_findings", [])
    contradictory_rules = issues.get("contradictory_rules", [])
    incompatible_recommendations = issues.get("incompatible_recommendations", [])

    if missing_evidence:
        raise ReasoningHealthError(
            f"Existen {len(missing_evidence)} razonamientos sin evidencia"
        )
    if invalid_confidence:
        raise ReasoningHealthError(
            f"Existen {len(invalid_confidence)} razonamientos con confidence inválido"
        )
    if duplicate_findings:
        raise ReasoningHealthError(
            f"Existen {len(duplicate_findings)} razonamientos con hallazgos duplicados"
        )
    if contradictory_rules:
        raise ReasoningHealthError(
            f"Existen {len(contradictory_rules)} razonamientos con reglas contradictorias"
        )
    if incompatible_recommendations:
        raise ReasoningHealthError(
            f"Existen {len(incompatible_recommendations)} razonamientos con recomendaciones incompatibles"
        )

    return {
        "incomplete_objects_count": len(issues.get("incomplete_objects", [])),
        "missing_evidence_count": len(missing_evidence),
        "invalid_confidence_count": len(invalid_confidence),
        "duplicate_findings_count": len(duplicate_findings),
        "contradictory_rules_count": len(contradictory_rules),
        "incompatible_recommendations_count": len(incompatible_recommendations),
        "status": "healthy",
    }
