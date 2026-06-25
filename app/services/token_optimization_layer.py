import re
import time
import unicodedata
from dataclasses import dataclass

from app.schemas.token_optimization_demo import (
    ExecutiveQuestionDemo,
    SimpleQuestionDemo,
    TokenOptimizationDemo,
)
from app.services.intent_router import Intent


def _elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)


@dataclass(frozen=True)
class TokenOptimizationMatch:
    intent: Intent
    confidence: float
    answer: str
    demo: TokenOptimizationDemo


class TokenOptimizationLayer:
    CONFIDENCE = 1.0

    ANSWER = (
        "La plataforma incorpora capas intermedias para evitar enviar todas las "
        "consultas a un modelo de lenguaje.\n\n"
        "Preguntas como:\n\n"
        "• Hola\n"
        "• ¿Quién eres?\n"
        "• ¿Qué información tienes?\n"
        "• ¿Qué KPIs tienes?\n\n"
        "se responden localmente sin consumir tokens del modelo.\n\n"
        "Esto reduce costos, mejora tiempos de respuesta y disminuye la "
        "dependencia de proveedores externos.\n\n"
        "Por ejemplo, una consulta interpretativa puede requerir cientos o "
        "miles de tokens de contexto, mientras que una respuesta determinística "
        "puede resolverse en milisegundos sin utilizar un modelo generativo.\n\n"
        "La arquitectura actual busca reservar el uso del modelo para consultas "
        "que realmente requieren análisis o generación de lenguaje."
    )

    PATTERNS: tuple[str, ...] = (
        "como optimizas el consumo de tokens",
        "como optimizas tokens",
        "como optimizas el consumo de token",
        "por que no envias todo al llm",
        "por que no mandas todo al llm",
        "por que no envias todo al modelo",
        "por que tienes capas intermedias",
        "por que existen capas intermedias",
        "como reduces costos",
        "como reduces los costos",
        "como reduce costos",
    )

    # Demostración ejecutiva de ahorro potencial de tokens (respuesta determinística).
    SIMPLE_QUESTION_TOKENS_IF_LLM = 800
    SIMPLE_QUESTION_TEXT = "¿Qué KPIs tienes?"

    # Referencia documentada del PoC: PromptAudit + observabilidad (EXECUTIVE_INSIGHTS).
    # Fuente: prompt_metrics.estimated_tokens y timings.llm_ms en consultas ejecutivas.
    EXECUTIVE_QUESTION_TEXT = "¿De qué insights hablas?"
    EXECUTIVE_PROMPT_TOKENS = 1228
    EXECUTIVE_LLM_MS = 52000

    def process(
        self,
        text: str,
        *,
        alternate_text: str | None = None,
        timings: object | None = None,
    ) -> TokenOptimizationMatch | None:
        started = time.perf_counter()
        candidates = [text]
        if alternate_text and alternate_text.strip() and alternate_text.strip() != text.strip():
            candidates.append(alternate_text)

        for candidate in candidates:
            normalized = self._normalize(candidate)
            if normalized and self._matches(normalized):
                if timings is not None:
                    timings.token_optimization_ms = _elapsed_ms(started)
                return TokenOptimizationMatch(
                    intent=Intent.TOKEN_OPTIMIZATION,
                    confidence=self.CONFIDENCE,
                    answer=self.ANSWER,
                    demo=self._build_demo(),
                )

        if timings is not None:
            timings.token_optimization_ms = _elapsed_ms(started)
        return None

    def _build_demo(self) -> TokenOptimizationDemo:
        tokens_if_llm = self.SIMPLE_QUESTION_TOKENS_IF_LLM
        tokens_actual = 0
        saving = 100 if tokens_if_llm > 0 else 0
        return TokenOptimizationDemo(
            simple_question=SimpleQuestionDemo(
                question=self.SIMPLE_QUESTION_TEXT,
                tokens_if_llm=tokens_if_llm,
                tokens_actual=tokens_actual,
                saving_percent=saving,
            ),
            executive_question=ExecutiveQuestionDemo(
                question=self.EXECUTIVE_QUESTION_TEXT,
                real_prompt_tokens=self.EXECUTIVE_PROMPT_TOKENS,
                llm_time_ms=self.EXECUTIVE_LLM_MS,
            ),
        )

    def _matches(self, normalized: str) -> bool:
        return any(
            normalized == pattern or normalized.startswith(f"{pattern} ")
            for pattern in self.PATTERNS
        )

    @staticmethod
    def _normalize(text: str) -> str:
        lowered = text.lower().strip()
        decomposed = unicodedata.normalize("NFD", lowered)
        without_accents = "".join(
            char for char in decomposed if unicodedata.category(char) != "Mn"
        )
        cleaned = re.sub(r"[^\w\s]", " ", without_accents)
        return re.sub(r"\s+", " ", cleaned).strip()
