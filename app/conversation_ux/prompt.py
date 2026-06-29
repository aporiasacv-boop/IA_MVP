CONVERSATION_PROMPT_MARKER = "OLNATURA_CONVERSATION_REDACTOR_V1"

SYSTEM_INSTRUCTIONS = """\
Eres el redactor conversacional de Olnatura Intelligence.
Tu rol es pulir la redacción de respuestas ya validadas por el sistema, manteniendo
la voz de un Director de Inteligencia Empresarial.
NO eres analista de datos: no calculas, no consultas bases de datos y no infieres hechos nuevos.

Reglas obligatorias:
- Nunca inventes datos, cifras, nombres ni conclusiones.
- Nunca modifiques cifras ni fechas recibidas.
- Nunca ocultes limitaciones presentes en el contexto.
- Nunca digas que eres un modelo de IA, ChatGPT, OpenAI, Ollama ni un chatbot.
- Nunca uses tono de FAQ, menú de opciones ni documentación técnica.
- Mantén tono ejecutivo, claro, confiable y con cercanía profesional.
- Sé breve: máximo 4 párrafos cortos.
- Invita a continuar el análisis con naturalidad.
- Utiliza únicamente la información recibida en el contexto.
- Responde en español.
- No uses encabezados técnicos ni formato de informe.
- Devuelve únicamente el texto de la respuesta final, sin prefijos ni explicaciones meta.
"""


def build_conversation_response_prompt(context) -> str:
    snapshot_lines = _format_snapshot_lines(context.dataset_snapshot)
    capabilities = "\n".join(f"- {item}" for item in context.capabilities) or "- No especificadas"
    examples = "\n".join(f"- {item}" for item in context.capability_examples) or "- No especificadas"
    suggestions = "\n".join(f"- {item}" for item in context.suggested_questions) or "- No especificadas"
    metadata_lines = _format_metadata_lines(context.pipeline_metadata)

    return f"""{CONVERSATION_PROMPT_MARKER}

{SYSTEM_INSTRUCTIONS}

PREGUNTA DEL USUARIO:
{context.user_message}

INTENCIÓN CONVERSACIONAL:
{context.conversation_category.value}

RESPUESTA ORIGINAL DEL PIPELINE (referencia, no ampliar):
{context.pipeline_answer}

BORRADOR VALIDADO A MEJORAR:
{context.template_answer}

DATOS VALIDADOS DEL DATASET:
{snapshot_lines}

CAPACIDADES DISPONIBLES:
{capabilities}

EJEMPLOS DE CONSULTA SOPORTADOS:
{examples}

PREGUNTAS SUGERIDAS DISPONIBLES (puedes invitar a una, no listar todas):
{suggestions}

CONTEXTO ADICIONAL DEL PIPELINE:
{metadata_lines}

Redacta la respuesta final conversacional:
"""


def _format_snapshot_lines(snapshot: dict) -> str:
    if not snapshot:
        return "- Sin cifras validadas disponibles en este momento."
    labels = {
        "registros": "movimientos contables",
        "clientes": "clientes",
        "proveedores": "proveedores",
        "cuentas": "cuentas contables",
        "fecha_minima": "fecha mínima",
        "fecha_maxima": "fecha máxima",
    }
    lines: list[str] = []
    for key, label in labels.items():
        value = snapshot.get(key)
        if value is not None:
            lines.append(f"- {label}: {value}")
    return "\n".join(lines) if lines else "- Sin cifras validadas disponibles en este momento."


def _format_metadata_lines(metadata: dict) -> str:
    if not metadata:
        return "- Sin metadatos adicionales."
    allowed = (
        "handled_by",
        "query_type",
        "fallback_type",
        "confidence",
        "knowledge_source",
        "knowledge_category",
    )
    lines = [
        f"- {key}: {metadata[key]}"
        for key in allowed
        if key in metadata and metadata[key] is not None
    ]
    return "\n".join(lines) if lines else "- Sin metadatos adicionales."
