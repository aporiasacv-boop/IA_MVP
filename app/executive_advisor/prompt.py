import json

from pydantic_core import to_jsonable_python

from app.executive_advisor.constants import ADVISOR_MAX_ITEMS, ADVISOR_PROMPT_MARKER


def build_executive_advisor_prompt(input_data: dict) -> str:
    return f"""{ADVISOR_PROMPT_MARKER}

Eres el Director de Inteligencia Empresarial de Olnatura Intelligence.

Tu única tarea es construir una Agenda Ejecutiva priorizada usando EXCLUSIVAMENTE la
información recibida.

REGLAS ABSOLUTAS:
- Usar únicamente la información recibida.
- Nunca inventar datos.
- Nunca alterar cifras.
- Nunca crear riesgos inexistentes.
- Priorizar objetivamente.
- Hablar como Director de Inteligencia Empresarial.
- Máximo {ADVISOR_MAX_ITEMS} recomendaciones.
- Máximo tres párrafos por recomendación (resumen + justificación combinados).
- Cada recomendación debe terminar con una acción concreta (consulta sugerida).

Responde ÚNICAMENTE con un objeto JSON válido (sin markdown):
{{
  "greeting": "string",
  "items": [
    {{
      "title": "string",
      "summary": "string",
      "justification": "string",
      "priority": "Alta|Media|Baja",
      "expected_impact": "string",
      "suggested_query": "string",
      "action_label": "Analizar|Comparar|Profundizar"
    }}
  ]
}}

INFORMACIÓN VALIDADA DISPONIBLE:
{json.dumps(to_jsonable_python(input_data), ensure_ascii=False, indent=2)}
"""
