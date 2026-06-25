import re
import time
import unicodedata
from dataclasses import dataclass

from app.services.intent_router import Intent


def _elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)


@dataclass(frozen=True)
class SocialMatch:
    intent: Intent
    confidence: float
    answer: str
    match_type: str = "social"


class SocialIdentityLayer:
    CONFIDENCE = 1.0

    GREETING_ANSWER = (
        "Hola.\n\n"
        "Soy el Asistente de Inteligencia Empresarial de Olnatura.\n\n"
        "Puedo ayudarte a consultar clientes, proveedores, indicadores, "
        "tendencias e insights empresariales."
    )

    IDENTITY_ANSWER = (
        "Soy el Asistente de Inteligencia Empresarial de Olnatura.\n\n"
        "Mi función es consultar, analizar y presentar información empresarial "
        "utilizando los datos disponibles en la plataforma."
    )

    CAPABILITIES_ANSWER = (
        "Puedo ayudarte a:\n\n"
        "• Consultar clientes\n"
        "• Consultar proveedores\n"
        "• Consultar cuentas contables\n"
        "• Consultar KPIs\n"
        "• Consultar tendencias\n"
        "• Generar insights empresariales\n"
        "• Resumir información del ejercicio analizado"
    )

    STATUS_ANSWER = (
        "Operativo y listo para responder consultas empresariales.\n\n"
        "Actualmente dispongo de información correspondiente al periodo "
        "disponible en la plataforma."
    )

    KNOWLEDGE_SCOPE_ANSWER = (
        "Actualmente dispongo de información relacionada con:\n\n"
        "• Clientes\n"
        "• Proveedores\n"
        "• Cuentas contables\n"
        "• Movimientos financieros\n"
        "• Indicadores empresariales\n"
        "• Tendencias\n"
        "• Insights ejecutivos\n\n"
        "No dispongo actualmente de información sobre productos, inventarios, "
        "producción o logística."
    )

    KPI_CATALOG_ANSWER = (
        "Actualmente puedo consultar:\n\n"
        "• Volumen económico total\n"
        "• Promedio mensual de actividad\n"
        "• Mes con mayor actividad\n"
        "• Mes con mayor volumen económico\n"
        "• Cliente principal\n"
        "• Proveedor principal\n"
        "• Cuenta principal\n"
        "• Participación Top 5 clientes\n"
        "• Participación Top 10 clientes"
    )

    INSIGHT_CATALOG_ANSWER = (
        "Actualmente puedo detectar:\n\n"
        "• Concentración de clientes\n"
        "• Cliente dominante\n"
        "• Proveedor dominante\n"
        "• Cuenta dominante\n"
        "• Mes con mayor actividad\n"
        "• Mes con mayor volumen\n"
        "• Crecimiento de clientes\n"
        "• Crecimiento de proveedores\n"
        "• Crecimiento de cuentas\n"
        "• Meses atípicos"
    )

    OUT_OF_SCOPE_ANSWER = (
        "Actualmente no dispongo de información sobre ese tema.\n\n"
        "Mi información actual incluye:\n\n"
        "• Clientes\n"
        "• Proveedores\n"
        "• Cuentas contables\n"
        "• KPIs\n"
        "• Tendencias\n"
        "• Insights empresariales\n\n"
        "La arquitectura está preparada para incorporar nuevas fuentes de "
        "información en futuras etapas."
    )

    OUT_OF_SCOPE_KEYWORDS: tuple[str, ...] = (
        "producto",
        "productos",
        "sku",
        "inventario",
        "inventarios",
        "almacen",
        "almacenes",
        "produccion",
        "lote",
        "lotes",
        "orden de fabricacion",
        "ordenes de fabricacion",
        "fabricacion",
        "logistica",
    )

    GREETING_PATTERNS: tuple[str, ...] = (
        r"^hola+$",
        r"^holaa+$",
        r"^ola+$",
        r"^hi$",
        r"^hello$",
        r"^buenos dias$",
        r"^buen dia$",
        r"^buenas tardes$",
        r"^buenas noches$",
        r"^que tal$",
        r"^que onda$",
        r"^saludos$",
    )

    IDENTITY_PATTERNS: tuple[str, ...] = (
        "quien eres",
        "que eres",
        "como te llamas",
        "eres una ia",
        "eres una inteligencia artificial",
        "quien te creo",
    )

    CAPABILITIES_PATTERNS: tuple[str, ...] = (
        "que haces",
        "para que sirves",
        "que puedes hacer",
        "como me ayudas",
        "que puedes responder",
        "cuales son tus capacidades",
    )

    STATUS_PATTERNS: tuple[str, ...] = (
        "como estas",
        "todo bien",
        "como va todo",
        "estas funcionando",
        "estas operativo",
    )

    KNOWLEDGE_SCOPE_PATTERNS: tuple[str, ...] = (
        "que informacion tienes",
        "que sabes",
        "que conoces",
        "de que puedes hablar",
        "que datos tienes",
        "que informacion manejas",
    )

    KPI_CATALOG_PATTERNS: tuple[str, ...] = (
        "que kpis tienes",
        "que kpi tienes",
        "que indicadores tienes",
        "que metricas tienes",
        "a que kpis te refieres",
        "a que kpi te refieres",
    )

    INSIGHT_CATALOG_PATTERNS: tuple[str, ...] = (
        "que insights tienes",
        "que insight tienes",
        "que hallazgos tienes",
        "a que insights te refieres",
        "que detectas",
        "que descubriste",
    )

    def process(
        self,
        text: str,
        *,
        alternate_text: str | None = None,
        timings: object | None = None,
    ) -> SocialMatch | None:
        total_started = time.perf_counter()
        candidates = [text]
        if alternate_text and alternate_text.strip() and alternate_text.strip() != text.strip():
            candidates.append(alternate_text)

        for index, candidate in enumerate(candidates):
            normalized = self._normalize(candidate)
            if not normalized:
                continue

            if index == 0:
                identity_started = time.perf_counter()
                identity_match = self._match_identity(normalized)
                if timings is not None:
                    timings.identity_layer_ms = _elapsed_ms(identity_started)
                if identity_match is not None:
                    if timings is not None:
                        timings.social_layer_ms = _elapsed_ms(total_started)
                    return identity_match
            elif self._match_identity(normalized) is not None:
                if timings is not None:
                    timings.social_layer_ms = _elapsed_ms(total_started)
                return self._match_identity(normalized)

            social_match = self._match_social(normalized)
            if social_match is not None:
                if timings is not None:
                    timings.social_layer_ms = _elapsed_ms(total_started)
                return social_match

        if timings is not None:
            timings.social_layer_ms = _elapsed_ms(total_started)
        return None

    def _match_social(self, normalized: str) -> SocialMatch | None:
        if self._is_out_of_scope(normalized):
            return self._build(Intent.OUT_OF_SCOPE, self.OUT_OF_SCOPE_ANSWER)

        checks: list[tuple[Intent, tuple[str, ...], str]] = [
            (Intent.GREETING, self.GREETING_PATTERNS, self.GREETING_ANSWER),
            (Intent.STATUS, self.STATUS_PATTERNS, self.STATUS_ANSWER),
            (Intent.KPI_CATALOG, self.KPI_CATALOG_PATTERNS, self.KPI_CATALOG_ANSWER),
            (Intent.INSIGHT_CATALOG, self.INSIGHT_CATALOG_PATTERNS, self.INSIGHT_CATALOG_ANSWER),
        ]

        for intent, patterns, answer in checks:
            if intent == Intent.GREETING:
                if self._matches_greeting(normalized):
                    return self._build(intent, answer)
                continue
            if self._matches_any(normalized, patterns):
                return self._build(intent, answer)
        return None

    def _match_identity(self, normalized: str) -> SocialMatch | None:
        if self._matches_any(normalized, self.IDENTITY_PATTERNS):
            return self._build(Intent.IDENTITY, self.IDENTITY_ANSWER, match_type="identity")
        return None

    def _is_out_of_scope(self, normalized: str) -> bool:
        return any(re.search(rf"\b{re.escape(keyword)}\b", normalized) for keyword in self.OUT_OF_SCOPE_KEYWORDS)

    def _matches_greeting(self, normalized: str) -> bool:
        return any(re.match(pattern, normalized) for pattern in self.GREETING_PATTERNS)

    @staticmethod
    def _matches_any(normalized: str, patterns: tuple[str, ...]) -> bool:
        return any(
            normalized == pattern or normalized.startswith(f"{pattern} ")
            for pattern in patterns
        )

    def _build(self, intent: Intent, answer: str, match_type: str = "social") -> SocialMatch:
        return SocialMatch(
            intent=intent,
            confidence=self.CONFIDENCE,
            answer=answer,
            match_type=match_type,
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
