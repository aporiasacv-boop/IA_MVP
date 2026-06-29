from app.ai_orchestration.constants import PROVIDER_MOCK
from app.ai_orchestration.providers.base import BaseLLMProvider
from app.ai_orchestration.schemas import LLMGenerateResult
from app.conversation_ux.prompt import CONVERSATION_PROMPT_MARKER
from app.executive_insight.constants import INSIGHT_PROMPT_MARKER
from app.business_copilot.constants import COPILOT_PROMPT_MARKER
from app.executive_advisor.constants import ADVISOR_PROMPT_MARKER
from app.executive_reasoning_v2.constants import REASONING_V2_PROMPT_MARKER
from app.core.settings import settings
from app.reasoning_engine.fallback import rule_based_decision
from app.reasoning_engine.prompt import REASONING_PROMPT_MARKER
from app.utils.text_normalizer import normalize_for_matching


class MockProvider(BaseLLMProvider):
    def __init__(self, model: str | None = None) -> None:
        self._model = model or "mock-executive-v1"

    def generate_response(self, prompt: str) -> LLMGenerateResult:
        if REASONING_PROMPT_MARKER in prompt:
            return self._generate_reasoning_response(prompt)
        if CONVERSATION_PROMPT_MARKER in prompt:
            return self._generate_conversation_response(prompt)
        if INSIGHT_PROMPT_MARKER in prompt:
            return self._generate_insight_response(prompt)
        if COPILOT_PROMPT_MARKER in prompt:
            return self._generate_copilot_response(prompt)
        if ADVISOR_PROMPT_MARKER in prompt:
            return self._generate_advisor_response(prompt)
        if REASONING_V2_PROMPT_MARKER in prompt:
            return self._generate_reasoning_v2_response(prompt)
        return self._generate_executive_response(prompt)

    def _generate_reasoning_response(self, prompt: str) -> LLMGenerateResult:
        import json

        message = _extract_section(prompt, "MENSAJE DEL USUARIO")
        decision = rule_based_decision(message)
        text = json.dumps(
            {
                "intent": decision.intent,
                "confidence": decision.confidence,
                "recommended_route": decision.recommended_route,
                "explanation": decision.explanation,
            },
            ensure_ascii=False,
        )
        tokens_in = self.estimated_tokens(prompt)
        tokens_out = self.estimated_tokens(text)
        return LLMGenerateResult(
            text=text,
            tokens_input=tokens_in,
            tokens_output=tokens_out,
            model=self._model,
            provider=self.provider_name(),
        )

    def _generate_conversation_response(self, prompt: str) -> LLMGenerateResult:
        draft = _extract_section(prompt, "BORRADOR VALIDADO A MEJORAR")
        user_message = _extract_section(prompt, "PREGUNTA DEL USUARIO")
        if not draft.strip():
            draft = _extract_section(prompt, "RESPUESTA ORIGINAL DEL PIPELINE")
        normalized = normalize_for_matching(user_message)

        if normalized.startswith("hola") or normalized.startswith("buenos"):
            text = draft
        elif "quien eres" in normalized or "como te llamas" in normalized:
            text = draft
        elif "que puedes hacer" in normalized or "como estas" in normalized:
            text = draft
        elif normalized in {"adios", "hasta luego", "gracias", "muchas gracias"}:
            text = draft
        else:
            text = draft

        text = text.strip()
        tokens_in = self.estimated_tokens(prompt)
        tokens_out = self.estimated_tokens(text)
        return LLMGenerateResult(
            text=text,
            tokens_input=tokens_in,
            tokens_output=tokens_out,
            model=self._model,
            provider=self.provider_name(),
        )

    def _generate_insight_response(self, prompt: str) -> LLMGenerateResult:
        import json

        deterministic = _extract_section(
            prompt,
            "RESULTADO DETERMINÍSTICO (NO MODIFICAR NI CONTRADECIR)",
        )
        query_type = _extract_section(prompt, "TIPO DE CONSULTA")
        text = json.dumps(
            {
                "executive_summary": (
                    "El resultado validado describe la situación actual sin alterar las cifras "
                    "del pipeline empresarial."
                ),
                "business_interpretation": (
                    f"La consulta {query_type or 'empresarial'} confirma la evidencia disponible: "
                    f"{deterministic[:180].strip()}."
                ),
                "possible_risks": [],
                "recommendations": [
                    "Profundizar en los elementos principales del resultado para validar concentración.",
                    "Comparar el periodo actual con meses anteriores si se requiere tendencia.",
                ],
                "next_questions": [
                    "¿Qué porcentaje representan los primeros cinco elementos del ranking?",
                    "¿Cómo se compara este resultado con el mes anterior?",
                ],
            },
            ensure_ascii=False,
        )
        tokens_in = self.estimated_tokens(prompt)
        tokens_out = self.estimated_tokens(text)
        return LLMGenerateResult(
            text=text,
            tokens_input=tokens_in,
            tokens_output=tokens_out,
            model=self._model,
            provider=self.provider_name(),
        )

    def _generate_copilot_response(self, prompt: str) -> LLMGenerateResult:
        import json

        query_type = _extract_section(prompt, "TIPO DE CONSULTA").upper()
        proposals: list[dict[str, str]] = []

        if query_type == "TOP_CLIENTES":
            proposals = [
                {
                    "title": "Analizar concentración comercial",
                    "rationale": "Los primeros clientes concentran una parte importante de la actividad.",
                    "action_label": "Analizar",
                    "query": "¿Qué porcentaje representan los primeros cinco clientes?",
                    "proposal_type": "profundizar",
                }
            ]
        elif query_type == "TOP_PROVEEDORES":
            proposals = [
                {
                    "title": "Analizar dependencia de proveedores",
                    "rationale": "El ranking sugiere posible dependencia operativa.",
                    "action_label": "Analizar",
                    "query": "¿Qué porcentaje del volumen corresponde al proveedor principal?",
                    "proposal_type": "detectar_dependencia",
                }
            ]
        elif query_type == "KPIS":
            proposals = [
                {
                    "title": "Explicar indicador principal",
                    "rationale": "Los movimientos suelen concentrar la mayor parte del volumen.",
                    "action_label": "Explicar",
                    "query": "Muéstrame los principales clientes",
                    "proposal_type": "explicar",
                }
            ]
        elif query_type == "DATA_COVERAGE":
            proposals = [
                {
                    "title": "Consultar meses con menor cobertura",
                    "rationale": "Existe suficiente información para un comparativo temporal.",
                    "action_label": "Comparar",
                    "query": "¿Qué meses tienen menor actividad registrada?",
                    "proposal_type": "comparar",
                }
            ]
        elif not query_type or query_type == "NO DISPONIBLE":
            proposals = [
                {
                    "title": "Profundizar en clientes clave",
                    "rationale": "Después del resumen conviene revisar la concentración comercial.",
                    "action_label": "Profundizar",
                    "query": "Muéstrame los principales clientes",
                    "proposal_type": "continuar_conversacion",
                }
            ]

        text = json.dumps({"proposals": proposals}, ensure_ascii=False)
        tokens_in = self.estimated_tokens(prompt)
        tokens_out = self.estimated_tokens(text)
        return LLMGenerateResult(
            text=text,
            tokens_input=tokens_in,
            tokens_output=tokens_out,
            model=self._model,
            provider=self.provider_name(),
        )

    def _generate_reasoning_v2_response(self, prompt: str) -> LLMGenerateResult:
        import json

        goal = _extract_section(prompt, "OBJETIVO EMPRESARIAL")
        evidence = _extract_section(prompt, "EVIDENCIA DISPONIBLE")
        missing = _extract_section(prompt, "EVIDENCIA FALTANTE")
        text = json.dumps(
            {
                "executive_summary": (
                    f"Con la evidencia disponible puedo concluir sobre {goal or 'el objetivo empresarial'} "
                    "sin alterar las cifras del paquete."
                ),
                "findings": [
                    line.strip("- ").strip()
                    for line in evidence.splitlines()
                    if line.strip().startswith("-")
                ][:4]
                or ["La evidencia validada sustenta el análisis solicitado."],
                "interpretation": (
                    "La interpretación se limita estrictamente a los hechos incluidos en el paquete "
                    "de evidencia empresarial."
                ),
                "risks": ["Concentración o dependencia si la evidencia de ranking lo sugiere."],
                "opportunities": ["Profundizar en los elementos principales ya validados."],
                "recommendations": [
                    "Comparar el periodo actual con meses anteriores usando evidencia existente.",
                ],
                "limitations": [
                    missing if missing and missing != "ninguna declarada" else "Sin limitaciones adicionales declaradas."
                ],
                "next_analyses": [
                    "¿Qué porcentaje representan los primeros cinco elementos del ranking?",
                ],
            },
            ensure_ascii=False,
        )
        tokens_in = self.estimated_tokens(prompt)
        tokens_out = self.estimated_tokens(text)
        return LLMGenerateResult(
            text=text,
            tokens_input=tokens_in,
            tokens_output=tokens_out,
            model=self._model,
            provider=self.provider_name(),
        )

    def _generate_advisor_response(self, prompt: str) -> LLMGenerateResult:
        import json

        text = json.dumps(
            {
                "greeting": "Buenos días.",
                "items": [
                    {
                        "title": "Concentración comercial",
                        "summary": (
                            "Los cinco clientes principales representan una parte importante "
                            "de la actividad validada."
                        ),
                        "justification": "El ranking disponible sugiere revisar dependencia comercial.",
                        "priority": "Alta",
                        "expected_impact": "Reducir dependencia comercial.",
                        "suggested_query": "Muéstrame los principales clientes",
                        "action_label": "Analizar",
                    },
                    {
                        "title": "KPIs ejecutivos",
                        "summary": "Los indicadores agregados sintetizan la salud operativa.",
                        "justification": "Punto de partida recomendado para la jornada.",
                        "priority": "Alta",
                        "expected_impact": "Obtener una foto ejecutiva validada.",
                        "suggested_query": "KPIs",
                        "action_label": "Analizar",
                    },
                ],
            },
            ensure_ascii=False,
        )
        tokens_in = self.estimated_tokens(prompt)
        tokens_out = self.estimated_tokens(text)
        return LLMGenerateResult(
            text=text,
            tokens_input=tokens_in,
            tokens_output=tokens_out,
            model=self._model,
            provider=self.provider_name(),
        )

    def _generate_executive_response(self, prompt: str) -> LLMGenerateResult:
        tokens_in = self.estimated_tokens(prompt)
        summary = (
            "Resumen ejecutivo basado exclusivamente en la evidencia proporcionada. "
            "Los hallazgos y recomendaciones reflejan el paquete de evidencia empresarial."
        )
        analysis = (
            "Análisis detallado: la respuesta se limita a los hechos, señales, riesgos "
            "y recomendaciones incluidos en el paquete. No se ha consultado SQL ni fuentes externas."
        )
        text = f"RESUMEN EJECUTIVO:\n{summary}\n\nANÁLISIS DETALLADO:\n{analysis}"
        tokens_out = self.estimated_tokens(text)
        return LLMGenerateResult(
            text=text,
            tokens_input=tokens_in,
            tokens_output=tokens_out,
            model=self._model,
            provider=self.provider_name(),
        )

    def health(self) -> dict:
        return {"status": "healthy", "provider": self.provider_name(), "model": self._model}

    def estimated_cost(self, tokens_input: int, tokens_output: int) -> float:
        return 0.0

    def estimated_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)

    def provider_name(self) -> str:
        return PROVIDER_MOCK

    @property
    def model_name(self) -> str:
        return self._model


def _extract_section(prompt: str, title: str) -> str:
    marker = f"{title}:"
    start = prompt.find(marker)
    if start == -1:
        return ""
    start += len(marker)
    tail = prompt[start:].lstrip("\n")
    for end_marker in (
        "\n\nRUTAS VÁLIDAS",
        "\n\nJSON",
        "\n\nDATOS VALIDADOS DEL DATASET",
        "\n\nDATOS VALIDADOS",
        "\n\nCAPACIDADES DISPONIBLES",
        "\n\nEJEMPLOS DE CONSULTA",
        "\n\nPREGUNTAS SUGERIDAS",
        "\n\nCONTEXTO ADICIONAL",
        "\n\nPREGUNTAS YA REALIZADAS EN LA SESIÓN",
        "\n\nSUGERENCIAS EXISTENTES",
        "\n\nCONTEXTO CONVERSACIONAL",
        "\n\nCONTEXTO DEL DATASET",
        "\n\nCONTEXTO CONVERSACIONAL",
        "\n\nRedacta la respuesta",
    ):
        end = tail.find(end_marker)
        if end != -1:
            return tail[:end].strip()
    return tail.strip()
