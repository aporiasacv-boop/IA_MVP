from datetime import datetime

from app.executive_advisor.constants import (
    ADVISOR_MAX_ITEMS,
    PRIORITY_ALTA,
    PRIORITY_MEDIA,
)
from app.executive_advisor.schemas import AdvisorInput, ExecutiveAgenda, ExecutiveAgendaItem


def build_greeting() -> str:
    hour = datetime.now().hour
    if hour < 12:
        return "Buenos días."
    if hour < 19:
        return "Buenas tardes."
    return "Buenas noches."


def build_rule_based_agenda(advisor_input: AdvisorInput) -> ExecutiveAgenda:
    items: list[ExecutiveAgendaItem] = []
    dataset = advisor_input.dataset_summary or {}
    report = advisor_input.operational_report or {}
    scenario = advisor_input.financial_scenario or {}

    clientes = dataset.get("clientes")
    proveedores = dataset.get("proveedores")
    registros = dataset.get("registros")

    if clientes is not None:
        items.append(
            ExecutiveAgendaItem(
                title="Concentración comercial",
                summary=(
                    f"El dataset validado incluye {clientes:,} clientes activos. "
                    "Conviene revisar si la actividad se concentra en pocos participantes."
                ).replace(",", "."),
                justification="Los rankings permiten detectar dependencia comercial temprana.",
                priority=PRIORITY_ALTA,
                expected_impact="Reducir dependencia comercial.",
                suggested_query="Muéstrame los principales clientes",
                action_label="Analizar",
            )
        )

    if registros is not None:
        items.append(
            ExecutiveAgendaItem(
                title="Actividad reciente",
                summary=(
                    f"Existen {registros:,} movimientos validados en el periodo disponible."
                ).replace(",", "."),
                justification="La magnitud operativa contextualiza prioridades del día.",
                priority=PRIORITY_MEDIA,
                expected_impact="Alinear expectativas de volumen con la dirección.",
                suggested_query="KPIs",
                action_label="Analizar",
            )
        )

    if proveedores is not None:
        items.append(
            ExecutiveAgendaItem(
                title="Clientes principales",
                summary="El análisis de clientes y proveedores complementa la lectura ejecutiva.",
                justification="Comparar ambos rankings revela dependencias cruzadas.",
                priority=PRIORITY_MEDIA,
                expected_impact="Equilibrar riesgo comercial y de abastecimiento.",
                suggested_query="Muéstrame los principales proveedores",
                action_label="Analizar",
            )
        )

    items.append(
        ExecutiveAgendaItem(
            title="KPIs ejecutivos",
            summary="Los indicadores agregados sintetizan la salud operativa del dataset.",
            justification="Es el punto de partida recomendado antes de análisis detallados.",
            priority=PRIORITY_ALTA,
            expected_impact="Obtener una foto ejecutiva rápida y validada.",
            suggested_query="KPIs",
            action_label="Analizar",
        )
    )

    if scenario.get("name"):
        items.append(
            ExecutiveAgendaItem(
                title="Escenarios financieros",
                summary=(
                    f"El escenario {scenario['name']} está disponible para revisión estratégica."
                ),
                justification=str(
                    scenario.get("description")
                    or "La comparación de escenarios orienta decisiones de capacidad."
                ),
                priority=PRIORITY_MEDIA,
                expected_impact="Anticipar costo operativo según escala prevista.",
                suggested_query=f"Analizar impacto del escenario {scenario['name']}",
                action_label="Analizar",
            )
        )

    if advisor_input.last_query_type == "TOP_CLIENTES":
        items.insert(
            0,
            ExecutiveAgendaItem(
                title="Profundizar concentración",
                summary="El último resultado fue un ranking de clientes.",
                justification="El siguiente paso natural es cuantificar la concentración.",
                priority=PRIORITY_ALTA,
                expected_impact="Validar riesgo de dependencia comercial.",
                suggested_query="¿Qué porcentaje representan los primeros cinco clientes?",
                action_label="Profundizar",
            ),
        )

    if report.get("legacy_rate", 0) > 15:
        items.append(
            ExecutiveAgendaItem(
                title="Cobertura del canal empresarial",
                summary=(
                    f"La tasa de respuestas legacy es {report['legacy_rate']:.1f}%."
                ),
                justification="Una cobertura empresarial alta reduce incertidumbre operativa.",
                priority=PRIORITY_MEDIA,
                expected_impact="Mejorar confiabilidad de respuestas ejecutivas.",
                suggested_query="¿Cuál es la cobertura de datos disponible?",
                action_label="Comparar",
            )
        )

    for proposal in advisor_input.business_copilot_proposals[:1]:
        title = str(proposal.get("title", "")).strip()
        query = str(proposal.get("query", "")).strip()
        if title and query:
            items.insert(
                0,
                ExecutiveAgendaItem(
                    title=title,
                    summary=str(proposal.get("rationale", title)),
                    justification="Continuación lógica del último análisis.",
                    priority=PRIORITY_ALTA,
                    expected_impact="Avanzar en la línea investigativa actual.",
                    suggested_query=query,
                    action_label=str(proposal.get("action_label", "Analizar")),
                ),
            )

    deduped: list[ExecutiveAgendaItem] = []
    seen_queries: set[str] = set()
    for item in items:
        key = item.suggested_query.strip().lower()
        if key in seen_queries:
            continue
        seen_queries.add(key)
        deduped.append(item)
        if len(deduped) >= ADVISOR_MAX_ITEMS:
            break

    return ExecutiveAgenda(greeting=build_greeting(), items=deduped)
