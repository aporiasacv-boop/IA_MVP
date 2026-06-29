from app.conversation_ux.context import DatasetSnapshot


def _format_count(value: int | None, label: str) -> str | None:
    if value is None:
        return None
    return f"{value:,}".replace(",", ".") + f" {label}"


def _dataset_overview(snapshot: DatasetSnapshot) -> str:
    if not snapshot.has_counts:
        return (
            "Tengo acceso a datos corporativos estructurados sobre clientes, proveedores, "
            "cuentas contables, indicadores y actividad mensual."
        )

    parts: list[str] = []
    registros = _format_count(snapshot.registros, "movimientos contables")
    clientes = _format_count(snapshot.clientes, "clientes")
    proveedores = _format_count(snapshot.proveedores, "proveedores")
    for item in (registros, clientes, proveedores):
        if item:
            parts.append(item)

    overview = "Hoy puedo analizar " + ", ".join(parts) + "."
    if snapshot.period_label:
        overview += f" El periodo disponible abarca {snapshot.period_label}."
    return overview


def build_greeting_answer(greeting: str, snapshot: DatasetSnapshot) -> str:
    overview = _dataset_overview(snapshot)
    return (
        f"{greeting}. Soy Olnatura Intelligence, tu analista corporativo.\n\n"
        "Estoy listo para ayudarte a convertir datos empresariales en respuestas claras "
        "y accionables.\n\n"
        f"{overview}\n\n"
        "Cuéntame qué quieres revisar y te guío paso a paso."
    )


def build_casual_answer(snapshot: DatasetSnapshot) -> str:
    overview = _dataset_overview(snapshot)
    return (
        "Todo en orden y listo para analizar tu negocio.\n\n"
        "Soy Olnatura Intelligence: trabajo como un analista corporativo que responde "
        "con evidencia, no con suposiciones.\n\n"
        f"{overview}\n\n"
        "Si quieres, podemos empezar con un indicador, un cliente clave o un mes concreto."
    )


def build_identity_answer(snapshot: DatasetSnapshot) -> str:
    overview = _dataset_overview(snapshot)
    return (
        "Soy Olnatura Intelligence, el asistente de inteligencia empresarial de Olnatura.\n\n"
        "Mi rol es ayudarte a interpretar información corporativa con trazabilidad: "
        "distingo hechos de recomendaciones y te indico cuando la evidencia es limitada.\n\n"
        f"{overview}\n\n"
        "Puedes preguntarme por clientes, proveedores, actividad mensual, rankings "
        "o pedirme un panorama ejecutivo para orientar la conversación."
    )


def build_capabilities_answer(
    snapshot: DatasetSnapshot,
    capability_labels: list[str],
    example_questions: list[str],
) -> str:
    overview = _dataset_overview(snapshot)
    capability_lines = "\n".join(f"• {label}" for label in capability_labels[:6])
    example_lines = "\n".join(f"• {question}" for question in example_questions[:3])

    return (
        "Soy Olnatura Intelligence. Puedo actuar como tu analista corporativo para "
        "explorar el negocio con datos reales.\n\n"
        f"{overview}\n\n"
        "Estas son algunas áreas que puedo analizar ahora:\n"
        f"{capability_lines}\n\n"
        "Para empezar con rapidez, puedes probar preguntas como:\n"
        f"{example_lines}"
    )


def build_executive_general_answer(snapshot: DatasetSnapshot) -> str:
    overview = _dataset_overview(snapshot)
    return (
        "Puedo darte una primera lectura ejecutiva del negocio con la información "
        "disponible hoy.\n\n"
        f"{overview}\n\n"
        "Mi enfoque es ayudarte a priorizar: identificar clientes y proveedores "
        "relevantes, revisar actividad por periodo y detectar señales de concentración "
        "o cambios relevantes.\n\n"
        "Si prefieres un arranque rápido, dime si quieres un panorama general, "
        "un mes específico o un actor clave del negocio."
    )


def build_help_answer(snapshot: DatasetSnapshot) -> str:
    overview = _dataset_overview(snapshot)
    return (
        "Con gusto te oriento.\n\n"
        "Funciono como un analista corporativo conversacional: escribes en lenguaje natural "
        "y yo interpreto la consulta, busco evidencia y te devuelvo una respuesta clara.\n\n"
        f"{overview}\n\n"
        "Puedes empezar con una pregunta directa sobre clientes, proveedores o un periodo, "
        "o pedirme sugerencias para explorar el negocio."
    )


def build_farewell_answer(snapshot: DatasetSnapshot) -> str:
    overview = _dataset_overview(snapshot)
    return (
        "Ha sido un gusto apoyarte.\n\n"
        "Cuando quieras retomar el análisis, estaré disponible para ayudarte con clientes, "
        "proveedores, indicadores y tendencias del negocio.\n\n"
        f"{overview}"
    )


def build_introduction_answer(snapshot: DatasetSnapshot) -> str:
    overview = _dataset_overview(snapshot)
    return (
        "Soy Olnatura Intelligence, el asistente de inteligencia empresarial de Olnatura.\n\n"
        "Transformo datos corporativos en respuestas claras para apoyar decisiones ejecutivas, "
        "siempre con base en evidencia disponible.\n\n"
        f"{overview}\n\n"
        "Puedes saludarme, preguntarme qué puedo hacer o ir directo a una consulta de negocio."
    )


def build_social_answer(snapshot: DatasetSnapshot) -> str:
    overview = _dataset_overview(snapshot)
    return (
        "Gracias por tu mensaje. Me alegra poder apoyarte.\n\n"
        "Sigo disponible para continuar el análisis empresarial cuando lo necesites.\n\n"
        f"{overview}"
    )
