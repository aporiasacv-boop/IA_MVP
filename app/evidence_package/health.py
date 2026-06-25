class EvidencePackageHealthError(ValueError):
    """Invariante de salud del paquete de evidencia violada."""


def validate_evidence_health(issues: dict) -> dict:
    missing_evidence = issues.get("missing_evidence", [])
    missing_eko = issues.get("missing_eko", [])
    missing_ero = issues.get("missing_ero", [])
    invalid_confidence = issues.get("invalid_confidence", [])
    duplicate_evidence = issues.get("duplicate_evidence", [])
    inconsistent_limitations = issues.get("inconsistent_limitations", [])

    if missing_evidence:
        raise EvidencePackageHealthError(
            f"Existen {len(missing_evidence)} paquetes sin evidencia"
        )
    if missing_eko:
        raise EvidencePackageHealthError(
            f"Existen {len(missing_eko)} paquetes sin EKO cuando se requería"
        )
    if missing_ero:
        raise EvidencePackageHealthError(
            f"Existen {len(missing_ero)} paquetes sin ERO cuando se requería"
        )
    if invalid_confidence:
        raise EvidencePackageHealthError(
            f"Existen {len(invalid_confidence)} paquetes con confidence inválido"
        )
    if duplicate_evidence:
        raise EvidencePackageHealthError(
            f"Existen {len(duplicate_evidence)} paquetes con evidencia duplicada"
        )
    if inconsistent_limitations:
        raise EvidencePackageHealthError(
            f"Existen {len(inconsistent_limitations)} paquetes con limitaciones inconsistentes"
        )

    return {
        "missing_evidence_count": len(missing_evidence),
        "missing_eko_count": len(missing_eko),
        "missing_ero_count": len(missing_ero),
        "invalid_confidence_count": len(invalid_confidence),
        "duplicate_evidence_count": len(duplicate_evidence),
        "inconsistent_limitations_count": len(inconsistent_limitations),
        "status": "healthy",
    }
