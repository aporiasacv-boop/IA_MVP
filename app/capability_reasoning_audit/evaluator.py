from app.capability_reasoning_audit.constants import (
    AUDIT_CLASSIFICATION_CORRECT,
    AUDIT_CLASSIFICATION_INCORRECT,
    AUDIT_CLASSIFICATION_PARTIAL,
    COMPATIBILITY_COMPATIBLE,
    COMPATIBILITY_PARTIAL,
)
from app.capability_reasoning_audit.schemas import (
    AuditedCapability,
    CapabilityDecision,
    CapabilityEvaluation,
)
from app.schemas.hybrid_chat import HybridChatResult


def evaluate_capability_outcome(
    *,
    capabilities: list[AuditedCapability],
    decision: CapabilityDecision,
    result: HybridChatResult,
) -> CapabilityEvaluation:
    compatible = [item for item in capabilities if item.compatibility == COMPATIBILITY_COMPATIBLE]
    partial = [item for item in capabilities if item.compatibility == COMPATIBILITY_PARTIAL]
    reusable = compatible + partial

    selected = decision.selected_capability
    selected_was_sufficient = (
        selected != "NONE"
        and any(item.capability_id == selected and item.compatibility == COMPATIBILITY_COMPATIBLE for item in capabilities)
    )
    reusable_exist = bool(reusable)
    could_combine = len({item.compatibility for item in reusable}) >= 1 and len(reusable) >= 2

    notes: list[str] = []
    for item in partial:
        notes.append(f"{item.capability_id} podía responder parcialmente.")
    for item in compatible:
        if item.capability_id != selected:
            notes.append(f"{item.capability_id} era compatible y no fue seleccionada.")

    if decision.fallback_used:
        if reusable_exist:
            classification = AUDIT_CLASSIFICATION_INCORRECT
            summary = "La consulta cayó en fallback aunque existían capacidades reutilizables."
        else:
            classification = AUDIT_CLASSIFICATION_CORRECT
            summary = "El fallback fue coherente: no había capabilities reutilizables claras."
    elif selected_was_sufficient and result.success:
        classification = AUDIT_CLASSIFICATION_CORRECT
        summary = "La capability elegida era suficiente para la intención detectada."
    elif selected != "NONE" and any(item.capability_id == selected for item in partial):
        classification = AUDIT_CLASSIFICATION_PARTIAL
        summary = "La capability elegida cubría parcialmente la intención."
    elif reusable_exist and selected == "NONE":
        classification = AUDIT_CLASSIFICATION_INCORRECT
        summary = "No se seleccionó capability aunque existían opciones reutilizables."
    elif result.success:
        classification = AUDIT_CLASSIFICATION_PARTIAL
        summary = "La ruta respondió, pero la afinidad con capabilities auditables fue limitada."
    else:
        classification = AUDIT_CLASSIFICATION_INCORRECT
        summary = "La respuesta no fue exitosa y la selección de capability no fue suficiente."

    return CapabilityEvaluation(
        selected_was_sufficient=selected_was_sufficient,
        reusable_capabilities_exist=reusable_exist,
        could_combine_capabilities=could_combine,
        classification=classification,
        summary=summary,
        notes=notes[:6],
    )
