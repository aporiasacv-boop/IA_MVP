from decimal import Decimal

from app.evidence_package.schemas import EnterpriseEvidencePackage, EvidenceItem


def _format_item(item: EvidenceItem) -> str:
    confidence = float(item.confidence) if item.confidence is not None else 0.0
    return f"- {item.key}: {item.value} (confianza: {confidence:.2f})"


def _section_lines(title: str, items: list[EvidenceItem]) -> list[str]:
    if not items:
        return []
    lines = [title]
    lines.extend(_format_item(item) for item in items)
    return lines


def _findings_from_package(package: EnterpriseEvidencePackage) -> list[EvidenceItem]:
    findings = [
        item for item in package.reasoning if item.key.startswith("findings:")
    ]
    if not findings:
        findings = list(package.facts)
    return findings


def _risks_from_package(package: EnterpriseEvidencePackage) -> list[EvidenceItem]:
    return [item for item in package.reasoning if item.key.startswith("risks:")]


def _opportunities_from_package(package: EnterpriseEvidencePackage) -> list[EvidenceItem]:
    return [
        item for item in package.reasoning if item.key.startswith("opportunities:")
    ]


def _business_context_text(package: EnterpriseEvidencePackage) -> str:
    ctx = package.business_context
    parts: list[str] = []
    if ctx.get("detected_context"):
        parts.append(f"Contexto: {ctx['detected_context']}")
    if ctx.get("detected_objects"):
        parts.append(f"Objetos: {', '.join(str(o) for o in ctx['detected_objects'])}")
    if ctx.get("entity_hints"):
        parts.append(f"Entidades mencionadas: {', '.join(str(h) for h in ctx['entity_hints'])}")
    if ctx.get("canonical_id"):
        parts.append(f"Entidad canónica resuelta: {ctx['canonical_id']}")
    if ctx.get("detected_timeframe"):
        parts.append(f"Periodo: {ctx['detected_timeframe']}")
    return "\n".join(parts) if parts else "Sin contexto empresarial adicional."


def build_executive_prompt(package: EnterpriseEvidencePackage) -> str:
    """Construye prompt legible únicamente desde EEP — sin SQL, JSON ni metadatos técnicos."""
    sections: list[str] = [
        "INSTRUCCIONES:",
        "Responde ÚNICAMENTE con la evidencia proporcionada.",
        "Si la evidencia es insuficiente, indícalo explícitamente.",
        "No inventes datos. No consultes fuentes externas.",
        "Estructura tu respuesta en RESUMEN EJECUTIVO y ANÁLISIS DETALLADO.",
        "",
        f"PREGUNTA:\n{package.question}",
        "",
        f"CONTEXTO EMPRESARIAL:\n{_business_context_text(package)}",
    ]

    for block in (
        _section_lines("HALLAZGOS:", _findings_from_package(package)),
        _section_lines("RIESGOS:", _risks_from_package(package)),
        _section_lines("OPORTUNIDADES:", _opportunities_from_package(package)),
        _section_lines("RECOMENDACIONES:", package.recommendations),
        _section_lines("SEÑALES:", package.signals),
        _section_lines("ALERTAS:", package.alerts),
    ):
        if block:
            sections.append("")
            sections.extend(block)

    if package.limitations:
        sections.append("")
        sections.append("LIMITACIONES:")
        for lim in package.limitations:
            sections.append(f"- [{lim.severity}] {lim.description}")

    avg_conf = float(package.confidence.average_confidence)
    sections.append("")
    sections.append(f"CONFIANZA DEL PAQUETE: {avg_conf:.4f}")
    sections.append(f"ELEMENTOS DE EVIDENCIA: {package.confidence.items_count}")

    evidence_keys = sorted(
        {item.key for item in package.knowledge + package.reasoning + package.facts}
    )
    if evidence_keys:
        sections.append("")
        sections.append("CLAVES DE EVIDENCIA DISPONIBLES (citar cuando corresponda):")
        for key in evidence_keys[:50]:
            sections.append(f"- {key}")

    return "\n".join(sections)


def package_confidence_value(package: EnterpriseEvidencePackage) -> Decimal:
    return package.confidence.average_confidence
