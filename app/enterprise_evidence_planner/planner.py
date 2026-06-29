from app.enterprise_evidence_planner.constants import (
    EVIDENCE_DEFINITIONS,
    EXECUTION_ORDER_WEIGHT,
    OPEN_QUERY_PROFILES,
    SIMPLE_QUERY_EVIDENCE,
)
from app.enterprise_evidence_planner.schemas import EnterpriseEvidencePlan, EvidenceItem
from app.reasoning_engine.constants import INTENT_BUSINESS_QUERY, INTENT_EXECUTIVE_ANALYSIS
from app.utils.text_normalizer import normalize_for_matching


def build_evidence_plan(
    *,
    question: str,
    intent: str | None,
    explanation: str | None,
) -> EnterpriseEvidencePlan:
    normalized = normalize_for_matching(question)
    simple = _match_simple_query(normalized)
    if simple is not None:
        evidence_key, goal = simple
        return _plan_from_keys(
            business_goal=goal,
            evidence_keys=(evidence_key,),
        )

    profile = _match_open_profile(normalized)
    if profile is not None:
        return _plan_from_keys(
            business_goal=str(profile["business_goal"]),
            evidence_keys=tuple(profile["evidence_keys"]),  # type: ignore[arg-type]
        )

    goal = _infer_default_goal(normalized, intent=intent, explanation=explanation)
    evidence_keys = _default_evidence_for_goal(normalized, intent=intent)
    return _plan_from_keys(business_goal=goal, evidence_keys=evidence_keys)


def _match_simple_query(normalized: str) -> tuple[str, str] | None:
    for patterns, evidence_key, goal in SIMPLE_QUERY_EVIDENCE:
        if any(pattern in normalized for pattern in patterns):
            return evidence_key, goal
    return None


def _match_open_profile(normalized: str) -> dict[str, object] | None:
    for profile in OPEN_QUERY_PROFILES:
        patterns = profile["patterns"]
        if any(pattern in normalized for pattern in patterns):  # type: ignore[arg-type]
            return profile
    return None


def _infer_default_goal(normalized: str, *, intent: str | None, explanation: str | None) -> str:
    if "cliente" in normalized:
        return "Analizar clientes"
    if "proveedor" in normalized:
        return "Analizar proveedores"
    if intent in {INTENT_EXECUTIVE_ANALYSIS, INTENT_BUSINESS_QUERY} and explanation:
        return explanation.rstrip(".")
    return "Responder decisión empresarial con evidencia existente"


def _default_evidence_for_goal(normalized: str, *, intent: str | None) -> tuple[str, ...]:
    if "cliente" in normalized:
        return ("principales_clientes", "kpis_negocio")
    if "proveedor" in normalized:
        return ("principales_proveedores", "conteo_proveedores")
    if intent == INTENT_EXECUTIVE_ANALYSIS:
        return ("kpis_negocio", "cobertura_temporal")
    return ("kpis_negocio",)


def _plan_from_keys(
    *,
    business_goal: str,
    evidence_keys: tuple[str, ...],
) -> EnterpriseEvidencePlan:
    items: list[EvidenceItem] = []
    labels: list[str] = []
    capabilities: list[str] = []
    missing: list[str] = []

    for key in evidence_keys:
        definition = EVIDENCE_DEFINITIONS.get(key)
        if definition is None:
            missing.append(key)
            continue
        label = str(definition["label"])
        capability = str(definition["capability"])
        items.append(EvidenceItem(evidence_id=key, label=label, capability=capability))
        labels.append(label)
        if capability not in capabilities:
            capabilities.append(capability)

    execution_order = sorted(
        capabilities,
        key=lambda capability: EXECUTION_ORDER_WEIGHT.get(capability, 99),
    )
    coverage = _estimate_coverage(len(items), len(evidence_keys))

    return EnterpriseEvidencePlan(
        business_goal=business_goal,
        required_evidence=labels,
        required_capabilities=capabilities,
        execution_order=execution_order,
        estimated_coverage=coverage,
        missing_evidence=missing,
        evidence_items=items,
    )


def _estimate_coverage(selected: int, requested: int) -> float:
    if requested == 0:
        return 0.0
    if selected == 1:
        return 88.0
    ratio = selected / requested
    base = 72.0 + (selected * 8.0)
    return min(96.0, round(base * ratio, 1))
