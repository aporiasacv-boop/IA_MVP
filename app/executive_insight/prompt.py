from app.executive_insight.constants import INSIGHT_PROMPT_MARKER


def build_executive_insight_prompt(
    *,
    user_question: str,
    query_type: str,
    deterministic_answer: str,
    confidence: float | None,
    dataset_snapshot: dict | None = None,
) -> str:
    snapshot_text = ""
    if dataset_snapshot:
        snapshot_text = "\n".join(
            f"- {key}: {value}" for key, value in dataset_snapshot.items() if value is not None
        )

    return f"""{INSIGHT_PROMPT_MARKER}

Eres un analista ejecutivo senior. Tu única tarea es interpretar un resultado empresarial
ya calculado de forma determinística.

REGLAS ABSOLUTAS:
- Nunca modifiques cifras.
- Nunca inventes indicadores.
- Nunca crees tendencias inexistentes.
- Nunca emitas conclusiones sin evidencia en el resultado recibido.
- Toda recomendación debe derivarse del resultado recibido.
- Si no existe suficiente información para un bloque, devuelve null o lista vacía.

Responde ÚNICAMENTE con un objeto JSON válido (sin markdown) con esta estructura:
{{
  "executive_summary": "string o null",
  "business_interpretation": "string o null",
  "possible_risks": ["string"],
  "recommendations": ["string"],
  "next_questions": ["string"]
}}

Las next_questions deben ser específicas al resultado (no genéricas).

PREGUNTA DEL USUARIO:
{user_question}

TIPO DE CONSULTA:
{query_type}

CONFIANZA DEL PIPELINE:
{confidence if confidence is not None else "no disponible"}

RESULTADO DETERMINÍSTICO (NO MODIFICAR NI CONTRADECIR):
{deterministic_answer}

CONTEXTO DEL DATASET (si existe):
{snapshot_text or "no disponible"}
"""
