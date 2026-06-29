from app.conversation_ux.classifier import ConversationCategory
from app.conversation_ux.context import DatasetSnapshot
from app.enterprise_personality.constants import (
    ADAPTATION_CLOSURE,
    ADAPTATION_CONSULTANT_MODE,
    ADAPTATION_DIRECT_ENGAGEMENT,
    ADAPTATION_EXPLORATION,
    ADAPTATION_GUIDED_RECOVERY,
    ADAPTATION_INSTITUTIONAL_INTRO,
)


def _format_count(value: int | None, label: str) -> str | None:
    if value is None:
        return None
    return f"{value:,}".replace(",", ".") + f" {label}"


def _dataset_brief(snapshot: DatasetSnapshot) -> str:
    if not snapshot.has_counts:
        return (
            "información corporativa estructurada sobre clientes, proveedores, "
            "cuentas contables e indicadores de actividad"
        )

    parts: list[str] = []
    for value, label in (
        (snapshot.registros, "movimientos contables"),
        (snapshot.clientes, "clientes"),
        (snapshot.proveedores, "proveedores"),
    ):
        formatted = _format_count(value, label)
        if formatted:
            parts.append(formatted)

    brief = ", ".join(parts)
    if snapshot.period_label:
        return f"{brief} ({snapshot.period_label})"
    return brief


def _dataset_context_line(snapshot: DatasetSnapshot) -> str:
    brief = _dataset_brief(snapshot)
    return f"Con la evidencia disponible hoy — {brief} —"


def render_personality_answer(
    *,
    category: ConversationCategory,
    adaptation_type: str,
    greeting: str,
    snapshot: DatasetSnapshot,
    capability_labels: list[str],
    example_questions: list[str],
) -> str:
    if category is ConversationCategory.GREETING:
        return _render_greeting(greeting, snapshot, adaptation_type)
    if category is ConversationCategory.CASUAL:
        return _render_casual(snapshot)
    if category is ConversationCategory.IDENTITY:
        return _render_identity(snapshot, adaptation_type)
    if category is ConversationCategory.CAPABILITIES:
        return _render_capabilities(snapshot, capability_labels, example_questions)
    if category is ConversationCategory.EXECUTIVE_GENERAL:
        return _render_executive(snapshot)
    if category is ConversationCategory.HELP:
        return _render_help(snapshot)
    if category is ConversationCategory.FAREWELL:
        return _render_farewell()
    if category is ConversationCategory.INTRODUCTION:
        return _render_introduction(snapshot)
    if category is ConversationCategory.SOCIAL:
        return _render_social()
    return ""


def _render_greeting(greeting: str, snapshot: DatasetSnapshot, adaptation_type: str) -> str:
    if adaptation_type == ADAPTATION_DIRECT_ENGAGEMENT:
        return (
            f"{greeting}. ¿Qué frente del negocio quieres examinar ahora?"
        )

    context = _dataset_context_line(snapshot)
    return (
        f"{greeting}. Soy Olnatura Intelligence — dirijo la inteligencia empresarial "
        f"de tu organización.\n\n"
        f"{context} estoy preparado para convertir señales en decisiones concretas.\n\n"
        "¿Por dónde orientamos el análisis?"
    )


def _render_casual(snapshot: DatasetSnapshot) -> str:
    context = _dataset_context_line(snapshot)
    return (
        "Operativamente, el panorama analítico está en orden.\n\n"
        f"{context} indícame si quieres revisar clientes, proveedores "
        "o un periodo específico."
    )


def _render_identity(snapshot: DatasetSnapshot, adaptation_type: str) -> str:
    context = _dataset_context_line(snapshot)
    if adaptation_type == ADAPTATION_DIRECT_ENGAGEMENT:
        return (
            "Soy Olnatura Intelligence, Director de Inteligencia Empresarial.\n\n"
            "Interpreto información corporativa con rigor analítico y trazabilidad "
            "de la evidencia.\n\n"
            "¿Qué aspecto del negocio quieres revisar?"
        )

    return (
        "Soy Olnatura Intelligence, Director de Inteligencia Empresarial en Olnatura.\n\n"
        "Mi función es traducir datos corporativos en lecturas accionables: "
        "distingo hechos verificables de recomendaciones y señalo el grado de evidencia "
        "disponible en cada respuesta.\n\n"
        f"{context} puedes consultarme sobre clientes, proveedores, actividad mensual "
        "o pedirme un panorama ejecutivo para orientar la conversación."
    )


def _render_capabilities(
    snapshot: DatasetSnapshot,
    capability_labels: list[str],
    example_questions: list[str],
) -> str:
    labels = [label for label in capability_labels if label.strip()][:4]
    areas = ", ".join(labels) if labels else "clientes, proveedores e indicadores clave"
    example = example_questions[0] if example_questions else "¿Qué pasó en junio?"
    context = _dataset_context_line(snapshot)

    return (
        "Olnatura Intelligence — desde inteligencia empresarial, puedo acompañarte en la lectura de "
        f"{areas}.\n\n"
        f"{context} estos frentes concentran el mayor valor analítico inmediato.\n\n"
        f"Para arrancar con impacto, te propongo comenzar con: «{example}»."
    )


def _render_executive(snapshot: DatasetSnapshot) -> str:
    context = _dataset_context_line(snapshot)
    return (
        "Puedo ofrecerte una lectura ejecutiva con la información disponible.\n\n"
        f"{context} mi recomendación es priorizar clientes y proveedores relevantes, "
        "revisar actividad por periodo y detectar señales de concentración.\n\n"
        "¿Prefieres un panorama general, un mes específico o un actor clave del negocio?"
    )


def _render_help(snapshot: DatasetSnapshot) -> str:
    context = _dataset_context_line(snapshot)
    return (
        "Entendido — te oriento.\n\n"
        "Plantea tu consulta con naturalidad; interpreto la intención, cruzo la evidencia "
        "disponible y te devuelvo una lectura clara del negocio.\n\n"
        f"{context} si lo prefieres, partimos por clientes, proveedores o un periodo concreto."
    )


def _render_farewell() -> str:
    return (
        "Ha sido un placer acompañarte en este análisis.\n\n"
        "Cuando quieras retomar, estaré disponible para profundizar en clientes, "
        "proveedores e indicadores del negocio."
    )


def _render_introduction(snapshot: DatasetSnapshot) -> str:
    context = _dataset_context_line(snapshot)
    return (
        "Soy Olnatura Intelligence — la capa de inteligencia empresarial de Olnatura.\n\n"
        "Transformo datos corporativos en lecturas ejecutivas con base en evidencia "
        "verificable.\n\n"
        f"{context} puedes ir directo a una consulta de negocio o pedirme orientación "
        "sobre el siguiente análisis."
    )


def _render_social() -> str:
    return (
        "Con gusto. Sigo a tu disposición para continuar el análisis empresarial "
        "cuando lo necesites."
    )


def sanitize_personality_text(text: str) -> str:
    lowered = text.lower()
    for phrase in (
        "soy un modelo de ia",
        "como inteligencia artificial",
        "como ia,",
        "no tengo emociones",
        "soy un chatbot",
        "soy un bot",
    ):
        if phrase in lowered:
            text = text.replace(phrase, "")
            text = text.replace(phrase.title(), "")
    return "\n".join(line for line in text.splitlines() if line.strip()).strip()
