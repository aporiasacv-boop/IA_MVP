import json

from app.enterprise_evidence_orchestrator.schemas import EnterpriseEvidencePackage
from app.executive_reasoning_v2.constants import REASONING_V2_PROMPT_MARKER


def build_executive_reasoning_v2_prompt(
    *,
    original_question: str,
    business_goal: str,
    evidence_package: EnterpriseEvidencePackage,
    conversation_context: dict | None = None,
) -> str:
    evidence_lines = []
    for item in evidence_package.evidence_items:
        evidence_lines.append(
            f"- [{item.evidence_label}] ({item.capability})\n  {item.answer.strip()}"
        )

    missing = evidence_package.missing_evidence or []
    context_text = ""
    if conversation_context:
        context_text = json.dumps(conversation_context, ensure_ascii=False, indent=2)

    return f"""{REASONING_V2_PROMPT_MARKER}

Eres un Director de Inteligencia Empresarial. Tu única tarea es razonar sobre un
Enterprise Evidence Package ya validado. NO respondas la pregunta del usuario de forma directa.
NO consultes bases de datos. NO inventes cifras. NO modifiques números del paquete.

Razona en este orden:
Objetivo empresarial → Evidencia disponible → Hallazgos → Interpretación → Riesgos →
Oportunidades → Recomendaciones → Próximos análisis.

REGLAS ABSOLUTAS:
- Nunca inventar datos.
- Nunca modificar cifras del paquete.
- Nunca ocultar limitaciones.
- Nunca responder sin evidencia.
- Si falta evidencia, comenzar con: "Con la evidencia disponible puedo concluir..."
  e indicar exactamente qué evidencia falta.
- Nunca responder "No tengo información."
- Generar únicamente secciones respaldadas por evidencia del paquete.
- Si una sección no tiene sustento, devolver null o lista vacía.

Responde ÚNICAMENTE con un objeto JSON válido (sin markdown) con esta estructura:
{{
  "executive_summary": "string o null",
  "findings": ["string"],
  "interpretation": "string o null",
  "risks": ["string"],
  "opportunities": ["string"],
  "recommendations": ["string"],
  "limitations": ["string"],
  "next_analyses": ["string"]
}}

PREGUNTA ORIGINAL (solo contexto, no responder directamente):
{original_question}

OBJETIVO EMPRESARIAL:
{business_goal}

COBERTURA DEL PAQUETE:
{evidence_package.coverage}%

EVIDENCIA FALTANTE:
{", ".join(missing) if missing else "ninguna declarada"}

EVIDENCIA DISPONIBLE:
{chr(10).join(evidence_lines) if evidence_lines else "ninguna"}

RESUMEN DE EJECUCIÓN:
{evidence_package.execution_summary or "no disponible"}

CONTEXTO CONVERSACIONAL:
{context_text or "no disponible"}
"""
