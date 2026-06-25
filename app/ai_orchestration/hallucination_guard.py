from dataclasses import dataclass

from app.ai_orchestration.constants import MIN_EVIDENCE_ITEMS
from app.evidence_package.schemas import EnterpriseEvidencePackage


@dataclass
class HallucinationGuardResult:
    triggered: bool
    reason: str | None = None
    insufficient_evidence: bool = False


CRITICAL_LIMITATION_CODES = frozenset({"missing_eko", "entity_unresolved"})


def evaluate_evidence_sufficiency(package: EnterpriseEvidencePackage) -> HallucinationGuardResult:
    evidence_count = len(package.evidence)
    item_count = (
        len(package.knowledge)
        + len(package.reasoning)
        + len(package.facts)
    )
    has_critical = any(
        lim.code in CRITICAL_LIMITATION_CODES and lim.severity in {"critical", "high"}
        for lim in package.limitations
    )
    if has_critical and item_count < MIN_EVIDENCE_ITEMS:
        return HallucinationGuardResult(
            triggered=True,
            reason="Limitaciones críticas y evidencia insuficiente en el paquete",
            insufficient_evidence=True,
        )
    if evidence_count == 0 and item_count < MIN_EVIDENCE_ITEMS:
        return HallucinationGuardResult(
            triggered=True,
            reason="El paquete no contiene evidencia suficiente para responder",
            insufficient_evidence=True,
        )
    return HallucinationGuardResult(triggered=False)


def validate_llm_response(text: str, package: EnterpriseEvidencePackage) -> HallucinationGuardResult:
    if not text or not text.strip():
        return HallucinationGuardResult(
            triggered=True,
            reason="Respuesta vacía del proveedor LLM",
        )
    lowered = text.lower()
    if "no hay evidencia suficiente" in lowered or "evidencia insuficiente" in lowered:
        return HallucinationGuardResult(triggered=False)
    evidence_keys = {item.key.lower() for item in package.knowledge + package.reasoning + package.facts}
    if not evidence_keys:
        return HallucinationGuardResult(triggered=False)
    cited = any(key.split(":", 1)[-1] in lowered or key in lowered for key in evidence_keys)
    if not cited and len(evidence_keys) > 0 and len(package.evidence) > 0:
        return HallucinationGuardResult(
            triggered=True,
            reason="La respuesta no cita evidencia del paquete",
        )
    return HallucinationGuardResult(triggered=False)


INSUFFICIENT_EVIDENCE_SUMMARY = (
    "No es posible generar un análisis ejecutivo: el paquete de evidencia "
    "no contiene información suficiente para responder con certeza."
)
INSUFFICIENT_EVIDENCE_ANALYSIS = (
    "El sistema detectó limitaciones críticas o ausencia de evidencia verificable. "
    "Se requiere completar el Enterprise Knowledge Object o el Enterprise Reasoning Object "
    "antes de solicitar un análisis ejecutivo."
)
