class KnowledgeHealthError(ValueError):
    """Invariante de salud del conocimiento empresarial violada."""


def validate_knowledge_health(issues: dict[str, list[dict]]) -> dict:
    invalid_confidence = issues.get("invalid_confidence", [])
    missing_evidence = issues.get("missing_evidence", [])
    empty_sections = issues.get("empty_sections", [])
    broken_relationships = issues.get("broken_relationships", [])
    contradictory_facts = issues.get("contradictory_facts", [])

    if invalid_confidence:
        raise KnowledgeHealthError(
            f"Existen {len(invalid_confidence)} objetos con confidence fuera de rango"
        )
    if missing_evidence:
        raise KnowledgeHealthError(
            f"Existen {len(missing_evidence)} objetos sin evidencia"
        )
    if empty_sections:
        raise KnowledgeHealthError(
            f"Existen {len(empty_sections)} objetos con secciones vacías"
        )
    if broken_relationships:
        raise KnowledgeHealthError(
            f"Existen {len(broken_relationships)} objetos con relaciones rotas"
        )
    if contradictory_facts:
        raise KnowledgeHealthError(
            f"Existen {len(contradictory_facts)} objetos con hechos contradictorios"
        )

    return {
        "incomplete_objects_count": len(issues.get("incomplete_objects", [])),
        "invalid_confidence_count": len(invalid_confidence),
        "missing_evidence_count": len(missing_evidence),
        "empty_sections_count": len(empty_sections),
        "broken_relationships_count": len(broken_relationships),
        "contradictory_facts_count": len(contradictory_facts),
        "status": "healthy",
    }
