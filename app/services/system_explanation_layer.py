import re
import time
import unicodedata
from dataclasses import dataclass

from app.services.intent_router import Intent


def _elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)


@dataclass(frozen=True)
class SystemExplanationMatch:
    intent: Intent
    confidence: float
    answer: str
    match_type: str = "system_explanation"


class SystemExplanationLayer:
    CONFIDENCE = 1.0

    EXECUTIVE_ANSWER = (
        "Mi función es transformar información empresarial en respuestas fáciles "
        "de consultar.\n\n"
        "Para ello utilizo una base de información previamente preparada a "
        "partir de los datos disponibles en la organización.\n\n"
        "Las consultas simples se responden mediante reglas e indicadores "
        "previamente calculados.\n\n"
        "Las consultas que requieren interpretación o narrativa utilizan un "
        "modelo de lenguaje para generar respuestas más naturales.\n\n"
        "Este enfoque permite reducir tiempos de respuesta, controlar costos y "
        "mantener consistencia en la información presentada."
    )

    TECHNICAL_ANSWER = (
        "El flujo general es:\n\n"
        "Pregunta\n"
        "↓\n"
        "Comprensión de lenguaje\n"
        "↓\n"
        "Clasificación de intención\n"
        "↓\n"
        "Consulta analítica\n"
        "↓\n"
        "Generación de respuesta\n\n"
        "No se realizan consultas directas a los sistemas transaccionales "
        "en cada interacción."
    )

    DATA_SOURCE_ANSWER = (
        "Actualmente utilizo información disponible dentro de la plataforma "
        "empresarial.\n\n"
        "La arquitectura está diseñada para integrar múltiples fuentes de "
        "información mediante una capa centralizada de datos, evitando depender "
        "directamente de los sistemas operativos para cada consulta."
    )

    DATA_SOURCE_PATTERNS: tuple[str, ...] = (
        "de donde salen los datos",
        "de donde sale la informacion",
        "de donde sale la data",
        "cual es tu fuente de informacion",
        "cual es tu fuente de datos",
        "quien te alimenta",
        "de donde obtienes la informacion",
        "de donde obtienes los datos",
    )

    SYSTEM_EXPLANATION_PATTERNS: tuple[str, ...] = (
        "como funcionas",
        "como trabajas",
        "como respondes",
        "como generas las respuestas",
        "como generas la respuesta",
        "como haces los calculos",
        "como haces los calculo",
        "como sabes eso",
        "como obtienes los resultados",
        "como obtienes el resultado",
        "usas inteligencia artificial para todo",
        "usas ia para todo",
        "utilizas inteligencia artificial para todo",
    )

    TECHNICAL_TRIGGERS: tuple[str, ...] = (
        "arquitectura",
        "tecnicamente",
        "infraestructura",
        "pipeline",
        "flujo",
    )

    def process(
        self,
        text: str,
        *,
        alternate_text: str | None = None,
        timings: object | None = None,
    ) -> SystemExplanationMatch | None:
        started = time.perf_counter()
        candidates = [text]
        if alternate_text and alternate_text.strip() and alternate_text.strip() != text.strip():
            candidates.append(alternate_text)

        for candidate in candidates:
            normalized = self._normalize(candidate)
            if not normalized:
                continue

            data_source = self._match_data_source(normalized)
            if data_source:
                if timings is not None:
                    timings.system_explanation_ms = _elapsed_ms(started)
                return data_source

            system_match = self._match_system_explanation(normalized, candidate)
            if system_match:
                if timings is not None:
                    timings.system_explanation_ms = _elapsed_ms(started)
                return system_match

        if timings is not None:
            timings.system_explanation_ms = _elapsed_ms(started)
        return None

    def _match_data_source(self, normalized: str) -> SystemExplanationMatch | None:
        if self._matches_any(normalized, self.DATA_SOURCE_PATTERNS):
            return SystemExplanationMatch(
                intent=Intent.DATA_SOURCE,
                confidence=self.CONFIDENCE,
                answer=self.DATA_SOURCE_ANSWER,
                match_type="data_source",
            )
        return None

    def _match_system_explanation(
        self,
        normalized: str,
        original: str,
    ) -> SystemExplanationMatch | None:
        if not self._matches_any(normalized, self.SYSTEM_EXPLANATION_PATTERNS):
            return None

        original_normalized = self._normalize(original)
        use_technical = self._has_technical_trigger(normalized) or self._has_technical_trigger(
            original_normalized
        )
        answer = self.TECHNICAL_ANSWER if use_technical else self.EXECUTIVE_ANSWER
        return SystemExplanationMatch(
            intent=Intent.SYSTEM_EXPLANATION,
            confidence=self.CONFIDENCE,
            answer=answer,
            match_type="technical" if use_technical else "executive",
        )

    def _has_technical_trigger(self, normalized: str) -> bool:
        return any(trigger in normalized for trigger in self.TECHNICAL_TRIGGERS)

    @staticmethod
    def _matches_any(normalized: str, patterns: tuple[str, ...]) -> bool:
        return any(
            normalized == pattern or normalized.startswith(f"{pattern} ")
            for pattern in patterns
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
