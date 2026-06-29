from app.capability_plan_executor.constants import (
    CLASSIFICATION_AVOIDABLE,
    CLASSIFICATION_CORRECT,
    CLASSIFICATION_NO_COMPATIBLE,
    CLASSIFICATION_PARTIALLY_AVOIDABLE,
    COVERAGE_FULL_THRESHOLD,
    COVERAGE_PARTIAL_THRESHOLD,
)
from app.capability_reasoner.engine import CapabilityReasoner
from app.reasoning_engine.fallback import rule_based_decision


FALLBACK_SCENARIO_CATALOG: tuple[tuple[str, str, str], ...] = (
    (
        "Analiza el universo de clientes",
        CLASSIFICATION_AVOIDABLE,
        "TOP_CLIENTES + KPIS",
    ),
    (
        "Háblame de los clientes",
        CLASSIFICATION_PARTIALLY_AVOIDABLE,
        "TOP_CLIENTES",
    ),
    (
        "Analiza nuestros proveedores",
        CLASSIFICATION_AVOIDABLE,
        "TOP_PROVEEDORES",
    ),
    (
        "¿Cuántos clientes existen?",
        CLASSIFICATION_CORRECT,
        "Pipeline directo (COUNT_CLIENTES)",
    ),
    (
        "Muéstrame los principales clientes",
        CLASSIFICATION_CORRECT,
        "Pipeline directo (TOP_CLIENTES)",
    ),
    (
        "¿Cuál es el sentido de la vida?",
        CLASSIFICATION_NO_COMPATIBLE,
        "OUT_OF_DOMAIN",
    ),
    (
        "No entiendo lo que me dices",
        CLASSIFICATION_CORRECT,
        "AMBIGUOUS / clarificación",
    ),
    (
        "¿Qué puedes hacer?",
        CLASSIFICATION_CORRECT,
        "Capacidades del sistema",
    ),
    (
        "Dame un resumen ejecutivo del negocio",
        CLASSIFICATION_PARTIALLY_AVOIDABLE,
        "KPIS + executive_reasoning",
    ),
    (
        "clientes proveedores junio todo",
        CLASSIFICATION_CORRECT,
        "AMBIGUOUS",
    ),
)


def classify_guided_fallback_scenarios() -> list[dict]:
    reasoner = CapabilityReasoner(enabled=True)
    rows: list[dict] = []

    for question, expected_class, notes in FALLBACK_SCENARIO_CATALOG:
        decision = rule_based_decision(question)
        metadata = decision.to_metadata()
        _, observability = reasoner.recommend(
            question=question,
            reasoning_decision=decision,
            metadata=metadata,
        )
        coverage = float(observability.get("estimated_coverage", 0))
        selected = observability.get("selected_capabilities", [])
        auto_class = _auto_classify(
            coverage=coverage,
            selected=selected,
            fallback_recommended=bool(observability.get("fallback_recommended", True)),
            question=question,
        )
        rows.append(
            {
                "question": question,
                "classification": auto_class,
                "expected": expected_class,
                "coverage": coverage,
                "selected_capabilities": selected,
                "notes": notes,
            }
        )

    return rows


def format_classification_report(rows: list[dict] | None = None) -> str:
    rows = rows or classify_guided_fallback_scenarios()
    lines = [
        "Clasificación de Guided Fallback — Sprint C/4",
        "=" * 48,
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"Consulta: {row['question']}",
                f"Clasificación: {row['classification']} (esperado: {row['expected']})",
                f"Cobertura reasoner: {row['coverage']}%",
                f"Capabilities: {', '.join(row['selected_capabilities']) or 'NONE'}",
                f"Notas: {row['notes']}",
                "",
            ]
        )
    return "\n".join(lines)


def _auto_classify(
    *,
    coverage: float,
    selected: list[str],
    fallback_recommended: bool,
    question: str,
) -> str:
    normalized = question.lower()
    if any(token in normalized for token in ("sentido de la vida", "filosof")):
        return CLASSIFICATION_NO_COMPATIBLE
    if coverage >= COVERAGE_FULL_THRESHOLD and selected:
        return CLASSIFICATION_AVOIDABLE
    if coverage >= COVERAGE_PARTIAL_THRESHOLD and selected:
        return CLASSIFICATION_PARTIALLY_AVOIDABLE
    if not fallback_recommended and selected:
        return CLASSIFICATION_AVOIDABLE
    if "no entiendo" in normalized or "que puedes hacer" in normalized:
        return CLASSIFICATION_CORRECT
    if coverage < COVERAGE_PARTIAL_THRESHOLD:
        return CLASSIFICATION_NO_COMPATIBLE if fallback_recommended else CLASSIFICATION_CORRECT
    return CLASSIFICATION_CORRECT
