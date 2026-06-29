from app.business_copilot.constants import COPILOT_PROMPT_MARKER, COPILOT_MAX_PROPOSALS


def build_business_copilot_prompt(
    *,
    user_question: str,
    query_type: str,
    deterministic_answer: str,
    executive_insight: dict | None,
    existing_suggestions: list[str],
    prior_questions: list[str],
    conversation_context: dict | None = None,
) -> str:
    insight_text = "no disponible"
    if executive_insight:
        insight_text = "\n".join(
            f"- {key}: {value}"
            for key, value in executive_insight.items()
            if value
        )

    context_text = "no disponible"
    if conversation_context:
        context_text = "\n".join(
            f"- {key}: {value}"
            for key, value in conversation_context.items()
            if value is not None
        )

    prior_text = "\n".join(f"- {question}" for question in prior_questions) or "ninguna"
    suggestions_text = "\n".join(f"- {question}" for question in existing_suggestions) or "ninguna"

    return f"""{COPILOT_PROMPT_MARKER}

Eres un Director de Inteligencia Empresarial. Tu única tarea es proponer el siguiente
análisis empresarial más útil, basándote exclusivamente en evidencia ya validada.

REGLAS ABSOLUTAS:
- No inventes datos.
- No crees nuevas conclusiones.
- No generes cifras nuevas.
- No inventes riesgos.
- Solo propón el siguiente análisis más útil derivado del resultado recibido.
- Máximo {COPILOT_MAX_PROPOSALS} propuestas.
- Nunca repitas preguntas ya realizadas en la conversación.
- Nunca propongas preguntas genéricas (ej. "¿Cuántos clientes existen?").
- Cada propuesta debe incluir una consulta concreta lista para ejecutar.

Tipos de propuesta válidos:
- profundizar
- comparar
- explicar
- detectar_dependencia
- continuar_conversacion

Responde ÚNICAMENTE con un objeto JSON válido (sin markdown):
{{
  "proposals": [
    {{
      "title": "string",
      "rationale": "string",
      "action_label": "string",
      "query": "string",
      "proposal_type": "profundizar|comparar|explicar|detectar_dependencia|continuar_conversacion"
    }}
  ]
}}

PREGUNTA DEL USUARIO:
{user_question}

TIPO DE CONSULTA:
{query_type or "no disponible"}

RESULTADO DETERMINÍSTICO:
{deterministic_answer}

LECTURA EJECUTIVA (si existe):
{insight_text}

PREGUNTAS YA REALIZADAS EN LA SESIÓN:
{prior_text}

SUGERENCIAS EXISTENTES (no repetir):
{suggestions_text}

CONTEXTO CONVERSACIONAL:
{context_text}
"""
