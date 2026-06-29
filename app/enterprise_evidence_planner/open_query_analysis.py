"""Análisis previo — consultas abiertas del Sprint D/4."""

from app.enterprise_evidence_planner.planner import build_evidence_plan


SPRINT_OPEN_QUERIES: tuple[str, ...] = (
    "¿Cómo ves nuestra cartera?",
    "Analiza el universo de clientes.",
    "¿Qué riesgos comerciales observas?",
    "¿Cómo está el negocio?",
    "¿Tenemos concentración de clientes?",
    "Analiza nuestros proveedores.",
)


def analyze_open_queries() -> list[dict]:
    rows: list[dict] = []
    for question in SPRINT_OPEN_QUERIES:
        plan = build_evidence_plan(
            question=question,
            intent="business_query",
            explanation="Consulta empresarial abierta.",
        )
        rows.append(
            {
                "question": question,
                "business_goal": plan.business_goal,
                "required_evidence": plan.required_evidence,
                "required_capabilities": plan.required_capabilities,
                "estimated_coverage": plan.estimated_coverage,
            }
        )
    return rows


def format_open_query_analysis(rows: list[dict] | None = None) -> str:
    rows = rows or analyze_open_queries()
    lines = ["Análisis de consultas abiertas — Sprint D/4", "=" * 44, ""]
    for row in rows:
        lines.extend(
            [
                f"Consulta: {row['question']}",
                f"Objetivo empresarial: {row['business_goal']}",
                f"Evidencia necesaria: {', '.join(row['required_evidence'])}",
                f"Capabilities: {', '.join(row['required_capabilities'])}",
                f"Cobertura estimada: {row['estimated_coverage']}%",
                "",
            ]
        )
    return "\n".join(lines)
