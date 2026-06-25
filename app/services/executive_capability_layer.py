import re
import time
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass

from app.services.intent_router import Intent


def _elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)


@dataclass(frozen=True)
class CapabilityMatch:
    intent: Intent
    confidence: float
    answer: str
    match_type: str = "capability"


class ExecutiveCapabilityLayer:
    CONFIDENCE = 1.0

    CAPABILITY_DISCOVERY_ANSWER = (
        "Actualmente puedo:\n\n"
        "• Consultar KPIs empresariales.\n"
        "• Analizar clientes, proveedores, cuentas y periodos.\n"
        "• Generar resúmenes ejecutivos.\n"
        "• Detectar tendencias, concentraciones y hallazgos.\n"
        "• Responder preguntas empresariales en lenguaje natural.\n"
        "• Explicar cómo funciona la plataforma y cómo optimiza costos."
    )

    INFORMATION_SCOPE_ANSWER = (
        "Actualmente dispongo de información relacionada con:\n\n"
        "• Clientes\n"
        "• Proveedores\n"
        "• Cuentas contables\n"
        "• Movimientos financieros\n"
        "• Indicadores empresariales\n"
        "• Tendencias e insights ejecutivos\n\n"
        "Puedo consultarla y analizarla en lenguaje natural dentro del periodo "
        "disponible en la plataforma."
    )

    LIMITATIONS_ANSWER = (
        "Actualmente no dispongo de:\n\n"
        "• Información de productos.\n"
        "• Inventarios.\n"
        "• SKU.\n"
        "• Márgenes.\n"
        "• EBITDA.\n"
        "• Información comercial que no exista dentro del dataset empresarial integrado.\n\n"
        "También existen capacidades aún no implementadas como análisis predictivo, "
        "forecasting y generación automática de gráficas."
    )

    SCOPE_ANSWER = (
        "Mi alcance actual se centra en información financiera y operativa integrada "
        "en la plataforma: clientes, proveedores, cuentas, KPIs, tendencias e insights.\n\n"
        "No cubro productos, inventarios, SKU, márgenes ni EBITDA. Tampoco realizo "
        "predicciones, forecasting ni generación automática de gráficas dentro del chat."
    )

    FEATURE_GRAFICAS_ANSWER = (
        "Actualmente la plataforma no genera gráficas directamente dentro del chat. "
        "Sin embargo, sí puede identificar KPIs, tendencias e indicadores que "
        "posteriormente pueden representarse visualmente."
    )

    FEATURE_DASHBOARDS_ANSWER = (
        "Actualmente no genero dashboards interactivos dentro del chat. "
        "Sí puedo presentar indicadores, rankings y hallazgos ejecutivos que "
        "pueden alimentar un tablero externo."
    )

    FEATURE_REPORTES_ANSWER = (
        "Puedo generar respuestas narrativas y resúmenes ejecutivos sobre la "
        "información disponible. No genero documentos descargables automáticos "
        "como reportes PDF o Word."
    )

    FEATURE_EXPORTAR_ANSWER = (
        "Actualmente no exporto información a archivos desde el chat. "
        "Los resultados se presentan como respuesta ejecutiva en la conversación."
    )

    FEATURE_EXCEL_ANSWER = (
        "No. Actualmente no exporto información a Excel desde el chat."
    )

    FEATURE_COMPARAR_MESES_ANSWER = (
        "Sí. Actualmente puedo comparar actividad y volumen entre distintos "
        "periodos disponibles en la información empresarial."
    )

    FEATURE_COMPARAR_ANOS_ANSWER = (
        "Sí. Puedo analizar y contrastar información por año cuando el periodo "
        "está disponible en el dataset integrado."
    )

    FEATURE_COMPARAR_CLIENTES_ANSWER = (
        "Sí. Puedo comparar clientes por volumen, participación, crecimiento y "
        "otros indicadores derivados de la información empresarial."
    )

    FEATURE_TENDENCIAS_ANSWER = (
        "Sí. Puedo analizar tendencias de actividad, volumen y concentración "
        "en clientes, proveedores, cuentas y periodos."
    )

    FEATURE_ANOMALIAS_ANSWER = (
        "Sí. Puedo detectar meses atípicos, variaciones relevantes y patrones "
        "inusuales a partir de los datos disponibles."
    )

    FEATURE_RIESGOS_ANSWER = (
        "Sí. Puedo identificar concentraciones, dependencias y patrones que "
        "pueden interpretarse como riesgos empresariales dentro del dataset disponible."
    )

    FEATURE_OPORTUNIDADES_ANSWER = (
        "Sí. Puedo señalar concentraciones, crecimientos y hallazgos que pueden "
        "interpretarse como oportunidades dentro del alcance actual del MVP."
    )

    FEATURE_RECOMENDACIONES_ANSWER = (
        "No. El MVP actual presenta hallazgos y análisis descriptivos, pero no "
        "formula recomendaciones accionables automatizadas."
    )

    FEATURE_PREDICCIONES_ANSWER = (
        "No. El MVP actual está orientado a análisis descriptivo y exploratorio. "
        "Las capacidades predictivas formarían parte de una fase posterior."
    )

    FEATURE_FORECASTING_ANSWER = FEATURE_PREDICCIONES_ANSWER

    FEATURE_PROYECCIONES_ANSWER = FEATURE_PREDICCIONES_ANSWER

    FEATURE_TRIGGERS: tuple[str, ...] = (
        "puedes",
        "podrias",
        "sabes",
        "soportas",
        "logras",
        "eres capaz",
        "se puede",
        "puede",
    )

    LIMITATIONS_PATTERNS: tuple[str, ...] = (
        "que no puedes hacer",
        "que no puedes",
        "que limitaciones tienes",
        "que limitaciones",
        "que informacion no tienes",
        "que datos te faltan",
        "que temas no conoces",
        "que no sabes",
        "que no puedes responder",
        "cual es tu alcance",
        "cual es el alcance",
    )

    INFORMATION_SCOPE_PATTERNS: tuple[str, ...] = (
        "que informacion tienes",
        "que informacion manejas",
        "que informacion puedes consultar",
        "que datos tienes",
        "que sabes",
        "que conoces",
        "de que puedes hablar",
        "que tipo de informacion tienes",
    )

    CAPABILITY_DISCOVERY_PATTERNS: tuple[str, ...] = (
        "que puedes hacer",
        "que sabes hacer",
        "para que sirves",
        "como puedes ayudarme",
        "como me ayudas",
        "que consultas soportas",
        "que tipo de preguntas respondes",
        "que tipo de analisis realizas",
        "que puedes analizar",
        "con que me puedes ayudar",
        "que haces",
        "cuales son tus capacidades",
        "que funciones tienes",
        "en que me puedes ayudar",
        "que puedes responder",
    )

    FEATURE_RULES: tuple[tuple[Callable[[str], bool], str, str], ...] = (
        (lambda n: "grafic" in n or "chart" in n, "graficas", FEATURE_GRAFICAS_ANSWER),
        (lambda n: "dashboard" in n, "dashboards", FEATURE_DASHBOARDS_ANSWER),
        (lambda n: "reporte" in n, "reportes", FEATURE_REPORTES_ANSWER),
        (lambda n: "excel" in n, "excel", FEATURE_EXCEL_ANSWER),
        (
            lambda n: ("export" in n or "descarg" in n) and "excel" not in n,
            "exportar",
            FEATURE_EXPORTAR_ANSWER,
        ),
        (lambda n: "compar" in n and "mes" in n, "comparar_meses", FEATURE_COMPARAR_MESES_ANSWER),
        (lambda n: "compar" in n and ("ano" in n or "ejercicio" in n), "comparar_anos", FEATURE_COMPARAR_ANOS_ANSWER),
        (lambda n: "compar" in n and "client" in n, "comparar_clientes", FEATURE_COMPARAR_CLIENTES_ANSWER),
        (lambda n: "tendenc" in n, "tendencias", FEATURE_TENDENCIAS_ANSWER),
        (lambda n: "anomal" in n or "atipic" in n, "anomalias", FEATURE_ANOMALIAS_ANSWER),
        (lambda n: "riesg" in n, "riesgos", FEATURE_RIESGOS_ANSWER),
        (lambda n: "oportunidad" in n, "oportunidades", FEATURE_OPORTUNIDADES_ANSWER),
        (lambda n: "recomend" in n, "recomendaciones", FEATURE_RECOMENDACIONES_ANSWER),
        (lambda n: "predic" in n, "predicciones", FEATURE_PREDICCIONES_ANSWER),
        (lambda n: "forecast" in n, "forecasting", FEATURE_FORECASTING_ANSWER),
        (lambda n: "proyecc" in n, "proyecciones", FEATURE_PROYECCIONES_ANSWER),
    )

    def process(
        self,
        text: str,
        *,
        alternate_text: str | None = None,
        timings: object | None = None,
    ) -> CapabilityMatch | None:
        started = time.perf_counter()
        candidates = [text]
        if alternate_text and alternate_text.strip() and alternate_text.strip() != text.strip():
            candidates.append(alternate_text)

        for candidate in candidates:
            normalized = self._normalize(candidate)
            if not normalized:
                continue

            limitation_match = self._match_limitations(normalized)
            if limitation_match is not None:
                if timings is not None:
                    timings.capability_layer_ms = _elapsed_ms(started)
                return limitation_match

            feature_match = self._match_feature_support(normalized)
            if feature_match is not None:
                if timings is not None:
                    timings.capability_layer_ms = _elapsed_ms(started)
                return feature_match

            discovery_match = self._match_capability_discovery(normalized)
            if discovery_match is not None:
                if timings is not None:
                    timings.capability_layer_ms = _elapsed_ms(started)
                return discovery_match

        if timings is not None:
            timings.capability_layer_ms = _elapsed_ms(started)
        return None

    def _match_limitations(self, normalized: str) -> CapabilityMatch | None:
        if self._matches_any(normalized, self.LIMITATIONS_PATTERNS):
            if normalized.startswith("cual es tu alcance") or normalized.startswith("cual es el alcance"):
                return self._build(Intent.LIMITATIONS, self.SCOPE_ANSWER, match_type="scope")
            return self._build(Intent.LIMITATIONS, self.LIMITATIONS_ANSWER, match_type="limitations")
        return None

    def _match_feature_support(self, normalized: str) -> CapabilityMatch | None:
        if not self._is_feature_question(normalized):
            return None

        for predicate, feature_key, answer in self.FEATURE_RULES:
            if predicate(normalized):
                return self._build(Intent.FEATURE_SUPPORT, answer, match_type=feature_key)
        return None

    def _match_capability_discovery(self, normalized: str) -> CapabilityMatch | None:
        if self._matches_any(normalized, self.CAPABILITY_DISCOVERY_PATTERNS):
            return self._build(
                Intent.CAPABILITY_DISCOVERY,
                self.CAPABILITY_DISCOVERY_ANSWER,
                match_type="capabilities",
            )

        if self._matches_any(normalized, self.INFORMATION_SCOPE_PATTERNS):
            return self._build(
                Intent.CAPABILITY_DISCOVERY,
                self.INFORMATION_SCOPE_ANSWER,
                match_type="information_scope",
            )
        return None

    def _is_feature_question(self, normalized: str) -> bool:
        return any(trigger in normalized for trigger in self.FEATURE_TRIGGERS)

    @staticmethod
    def _matches_any(normalized: str, patterns: tuple[str, ...]) -> bool:
        return any(
            normalized == pattern or normalized.startswith(f"{pattern} ")
            for pattern in patterns
        )

    def _build(self, intent: Intent, answer: str, match_type: str) -> CapabilityMatch:
        return CapabilityMatch(
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
