from app.capability_reasoner.constants import (
    COMBINATION_GAP,
    FALLBACK_COVERAGE_THRESHOLD,
    MIN_CANDIDATE_SCORE,
    MIN_PRIMARY_SCORE,
)
from app.capability_reasoner.schemas import CandidateCapability, CapabilityReasonerPlan


def build_reasoner_plan(
    *,
    reasoning_goal: str,
    candidates: list[CandidateCapability],
) -> CapabilityReasonerPlan:
    viable = [item for item in candidates if item.score >= MIN_CANDIDATE_SCORE]
    selected = _select_capabilities(viable)
    coverage = _estimate_coverage(selected)
    fallback_recommended = coverage < FALLBACK_COVERAGE_THRESHOLD
    recommended_plan = _build_recommendation(
        reasoning_goal=reasoning_goal,
        selected=selected,
        coverage=coverage,
        fallback_recommended=fallback_recommended,
    )

    return CapabilityReasonerPlan(
        reasoning_goal=reasoning_goal,
        candidate_capabilities=candidates,
        selected_capabilities=[item.capability_id for item in selected],
        estimated_coverage=round(coverage * 100, 1),
        recommended_plan=recommended_plan,
        fallback_recommended=fallback_recommended,
    )


def _select_capabilities(viable: list[CandidateCapability]) -> list[CandidateCapability]:
    if not viable:
        return []

    ranked = sorted(viable, key=lambda item: item.score, reverse=True)
    primary = ranked[0]
    if primary.score < MIN_PRIMARY_SCORE:
        return [primary] if primary.score >= MIN_CANDIDATE_SCORE else []

    selected = [primary]
    if len(ranked) > 1:
        secondary = ranked[1]
        if (
            secondary.score >= MIN_PRIMARY_SCORE
            and primary.score - secondary.score <= COMBINATION_GAP
            and _should_combine(primary.capability_id, secondary.capability_id)
        ):
            selected.append(secondary)

    return selected


def _should_combine(primary_id: str, secondary_id: str) -> bool:
    pairs = {
        frozenset({"TOP_CLIENTES", "KPIS"}),
        frozenset({"TOP_PROVEEDORES", "MAX_PROVEEDOR_MES"}),
        frozenset({"DATASET_INFO", "DATA_COVERAGE"}),
        frozenset({"COUNT_CLIENTES", "KPIS"}),
    }
    return frozenset({primary_id, secondary_id}) in pairs


def _estimate_coverage(selected: list[CandidateCapability]) -> float:
    if not selected:
        return 0.0
    if len(selected) == 1:
        return min(0.92, selected[0].score + 0.08)

    primary, secondary = selected[0], selected[1]
    combined = 1 - (1 - primary.score) * (1 - secondary.score * 0.85)
    return min(0.95, combined)


def _build_recommendation(
    *,
    reasoning_goal: str,
    selected: list[CandidateCapability],
    coverage: float,
    fallback_recommended: bool,
) -> str:
    coverage_pct = round(coverage * 100)

    if fallback_recommended:
        return (
            f"Con las capacidades existentes puedo cubrir aproximadamente el {coverage_pct}% "
            f"de la intención «{reasoning_goal}»; ninguna capability aporta valor suficiente. "
            "Se recomienda Guided Fallback."
        )

    if len(selected) == 1:
        item = selected[0]
        return (
            f"Con las capacidades existentes puedo cubrir aproximadamente el {coverage_pct}% "
            f"de la intención «{reasoning_goal}»; recomiendo utilizar {item.capability_id} "
            f"({item.label}) y evitar el fallback."
        )

    primary, secondary = selected[0], selected[1]
    return (
        f"Con las capacidades existentes puedo cubrir aproximadamente el {coverage_pct}% "
        f"de la intención «{reasoning_goal}»; recomiendo responder utilizando "
        f"{primary.capability_id} y complementar posteriormente con {secondary.capability_id}."
    )
