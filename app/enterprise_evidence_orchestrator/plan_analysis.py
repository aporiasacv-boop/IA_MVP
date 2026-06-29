"""Análisis de viabilidad del EnterpriseEvidencePlan — Sprint E/4."""

from app.enterprise_evidence_planner.planner import build_evidence_plan
from app.query_engine.query_catalog import QUERY_TYPE_EXAMPLE_QUESTIONS
from app.query_engine.query_types import BusinessQueryType


def analyze_plan_feasibility(question: str) -> dict:
    plan = build_evidence_plan(
        question=question,
        intent="business_query",
        explanation="Análisis de viabilidad del plan.",
    )
    executable: list[str] = []
    blocked: list[str] = []
    for capability in plan.execution_order:
        if _is_pipeline_executable(capability):
            executable.append(capability)
        else:
            blocked.append(capability)

    return {
        "question": question,
        "business_goal": plan.business_goal,
        "required_capabilities": plan.required_capabilities,
        "execution_order": plan.execution_order,
        "estimated_coverage": plan.estimated_coverage,
        "pipeline_executable": executable,
        "pipeline_blocked": blocked,
        "fully_executable": len(blocked) == 0 and bool(executable),
    }


def format_plan_feasibility_report(questions: list[str] | None = None) -> str:
    samples = questions or [
        "¿Cómo ves nuestra cartera?",
        "Analiza el universo de clientes.",
        "Analiza nuestros proveedores.",
        "¿Cuántos clientes existen?",
        "¿Cuál es el sentido de la vida?",
    ]
    lines = ["Análisis EnterpriseEvidencePlan — Sprint E/4", "=" * 44, ""]
    for question in samples:
        analysis = analyze_plan_feasibility(question)
        lines.extend(
            [
                f"Consulta: {analysis['question']}",
                f"Objetivo: {analysis['business_goal']}",
                f"Capabilities: {', '.join(analysis['required_capabilities']) or 'NONE'}",
                f"Orden: {', '.join(analysis['execution_order']) or 'NONE'}",
                f"Cobertura estimada: {analysis['estimated_coverage']}%",
                f"Ejecutables vía Pipeline: {', '.join(analysis['pipeline_executable']) or 'NONE'}",
                f"Bloqueadas: {', '.join(analysis['pipeline_blocked']) or 'NONE'}",
                f"Plan completamente ejecutable: {'Sí' if analysis['fully_executable'] else 'No'}",
                "",
            ]
        )
    return "\n".join(lines)


def _is_pipeline_executable(capability_id: str) -> bool:
    try:
        query_type = BusinessQueryType(capability_id)
    except ValueError:
        return False
    return query_type in QUERY_TYPE_EXAMPLE_QUESTIONS
