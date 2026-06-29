from app.capability_reasoning_audit.schemas import (
    AuditedCapability,
    CapabilityDecision,
    CapabilityEvaluation,
    CapabilityReasoningAuditReport,
)


def format_audit_report(
    *,
    question: str,
    intent: str | None,
    confidence: float | None,
    explanation: str | None,
    capabilities: list[AuditedCapability],
    decision: CapabilityDecision,
    evaluation: CapabilityEvaluation,
) -> str:
    lines = [
        "Consulta",
        "---------",
        question,
        "",
        "Intent",
        "------",
        intent or "—",
        "",
    ]

    if confidence is not None:
        lines.extend(["Confianza", "---------", f"{confidence:.2f}", ""])
    if explanation:
        lines.extend(["Explicación", "-----------", explanation, ""])

    lines.extend(["Capabilities disponibles", "-------------------------"])
    for item in capabilities:
        lines.append(f"{item.capability_id} [{item.compatibility}] — {item.label}")

    lines.extend(
        [
            "",
            "Capability elegida",
            "------------------",
            decision.selected_capability,
            "",
            "Ruta",
            "----",
            decision.final_route,
            "",
            "Evaluación",
            "-----------",
            evaluation.classification,
            evaluation.summary,
        ]
    )

    if evaluation.notes:
        lines.append("")
        lines.append("Notas")
        lines.append("-----")
        lines.extend(evaluation.notes)

    lines.extend(["", "Resultado", "----------", evaluation.summary])
    return "\n".join(lines)


def build_report(
    *,
    question: str,
    intent: str | None,
    confidence: float | None,
    explanation: str | None,
    capabilities: list[AuditedCapability],
    decision: CapabilityDecision,
    evaluation: CapabilityEvaluation,
) -> CapabilityReasoningAuditReport:
    report_text = format_audit_report(
        question=question,
        intent=intent,
        confidence=confidence,
        explanation=explanation,
        capabilities=capabilities,
        decision=decision,
        evaluation=evaluation,
    )
    return CapabilityReasoningAuditReport(
        question=question,
        intent=intent,
        confidence=confidence,
        explanation=explanation,
        available_capabilities=capabilities,
        decision=decision,
        evaluation=evaluation,
        report_text=report_text,
    )
