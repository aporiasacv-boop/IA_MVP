import re
import unicodedata
from dataclasses import dataclass
from enum import StrEnum


class Intent(StrEnum):
    TOP_CLIENTES = "TOP_CLIENTES"
    TOP_PROVEEDORES = "TOP_PROVEEDORES"
    TOP_CUENTAS = "TOP_CUENTAS"
    RESUMEN_MENSUAL = "RESUMEN_MENSUAL"
    KPIS = "KPIS"
    KPIS_EJECUTIVOS = "KPIS_EJECUTIVOS"
    INSIGHTS = "INSIGHTS"
    EVOLUCION_CLIENTE = "EVOLUCION_CLIENTE"
    EVOLUCION_PROVEEDOR = "EVOLUCION_PROVEEDOR"
    EVOLUCION_CUENTA = "EVOLUCION_CUENTA"
    MONTH_ANALYSIS = "MONTH_ANALYSIS"
    YEAR_SUMMARY = "YEAR_SUMMARY"
    EXECUTIVE_INSIGHTS = "EXECUTIVE_INSIGHTS"
    BUSINESS_CONCENTRATION = "BUSINESS_CONCENTRATION"
    GREETING = "GREETING"
    IDENTITY = "IDENTITY"
    STATUS = "STATUS"
    KPI_CATALOG = "KPI_CATALOG"
    INSIGHT_CATALOG = "INSIGHT_CATALOG"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    TOKEN_OPTIMIZATION = "TOKEN_OPTIMIZATION"
    SYSTEM_EXPLANATION = "SYSTEM_EXPLANATION"
    DATA_SOURCE = "DATA_SOURCE"
    KNOWLEDGE_SCOPE = "KNOWLEDGE_SCOPE"
    DATA_COVERAGE = "DATA_COVERAGE"
    CAPABILITIES = "CAPABILITIES"
    CAPABILITY_DISCOVERY = "CAPABILITY_DISCOVERY"
    FEATURE_SUPPORT = "FEATURE_SUPPORT"
    LIMITATIONS = "LIMITATIONS"
    BOTTOM_CLIENTES = "BOTTOM_CLIENTES"
    BOTTOM_PROVEEDORES = "BOTTOM_PROVEEDORES"
    BOTTOM_CUENTAS = "BOTTOM_CUENTAS"
    BEST_MONTH = "BEST_MONTH"
    WORST_MONTH = "WORST_MONTH"
    CLIENTE_CRECIMIENTO = "CLIENTE_CRECIMIENTO"
    CLIENTE_CAIDA = "CLIENTE_CAIDA"
    PROVEEDOR_CRECIMIENTO = "PROVEEDOR_CRECIMIENTO"
    PROVEEDOR_CAIDA = "PROVEEDOR_CAIDA"
    EXECUTIVE_SUMMARY = "EXECUTIVE_SUMMARY"
    RISKS = "RISKS"
    OPPORTUNITIES = "OPPORTUNITIES"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class IntentMatch:
    intent: Intent
    confidence: float
    entity_code: str | None = None
    match_type: str = "none"


INTENT_PATTERNS: list[tuple[Intent, tuple[str, ...]]] = [
    (
        Intent.KPIS_EJECUTIVOS,
        (
            "kpis ejecutivos",
            "kpi ejecutivos",
            "indicadores ejecutivos",
            "metricas ejecutivas",
            "dashboard ejecutivo",
            "resumen ejecutivo",
        ),
    ),
    (
        Intent.INSIGHTS,
        (
            "insights",
            "insight",
            "hallazgos",
            "hallazgo",
            "conclusiones",
            "conclusion",
            "inteligencia empresarial",
            "que paso raro",
        ),
    ),
    (
        Intent.RESUMEN_MENSUAL,
        (
            "resumen mensual",
            "resume los meses",
            "resumen de meses",
            "resumen por mes",
            "actividad mensual",
            "movimientos mensuales",
            "evolucion mensual general",
        ),
    ),
    (
        Intent.TOP_CLIENTES,
        (
            "mejor cliente",
            "cliente principal",
            "cliente dominante",
            "top clientes",
            "top cliente",
            "ranking clientes",
            "ranking de clientes",
            "principales clientes",
            "quien es nuestro mejor cliente",
            "cual es nuestro mejor cliente",
            "quien es el mejor cliente",
            "cual es el mejor cliente",
            "quien compra mas",
            "quien nos compra mas",
            "cliente mas grande",
        ),
    ),
    (
        Intent.TOP_PROVEEDORES,
        (
            "mejor proveedor",
            "proveedor principal",
            "proveedor dominante",
            "top proveedores",
            "top proveedor",
            "ranking proveedores",
            "ranking de proveedores",
            "principales proveedores",
            "quien es nuestro mejor proveedor",
            "cual es el proveedor principal",
            "cual es nuestro proveedor principal",
            "quien vende mas",
            "quien nos vende mas",
        ),
    ),
    (
        Intent.TOP_CUENTAS,
        (
            "mejor cuenta",
            "cuenta principal",
            "cuenta dominante",
            "top cuentas",
            "top cuenta",
            "ranking cuentas",
            "ranking de cuentas",
            "principales cuentas",
            "cuentas principales",
        ),
    ),
    (
        Intent.KPIS,
        (
            "kpis",
            "kpi",
            "indicadores clave",
            "indicadores generales",
            "metricas generales",
            "muestrame los kpis",
            "mostrar kpis",
            "mostrar los kpis",
        ),
    ),
]

RESUMEN_MENSUAL_KEYWORDS = ("meses", "por mes", "mensual")

HUMAN_INTENT_PATTERNS: list[tuple[Intent, tuple[str, ...]]] = [
    (
        Intent.LIMITATIONS,
        (
            "que no puedes hacer",
            "que limitaciones tienes",
            "que informacion no tienes",
            "que datos te faltan",
            "que temas no conoces",
            "que no sabes",
            "que no puedes responder",
            "cual es tu alcance",
        ),
    ),
    (
        Intent.CAPABILITY_DISCOVERY,
        (
            "que informacion tienes",
            "que sabes",
            "que datos tienes",
            "que conoces",
            "que puedes responder",
            "que informacion manejas",
            "que tipo de informacion tienes",
            "que puedes hacer",
            "que sabes hacer",
            "para que sirves",
            "como puedes ayudarme",
            "que consultas soportas",
            "que tipo de preguntas respondes",
            "que tipo de analisis realizas",
            "que puedes analizar",
            "con que me puedes ayudar",
            "cuales son tus capacidades",
            "que funciones tienes",
            "en que me puedes ayudar",
        ),
    ),
    (
        Intent.FEATURE_SUPPORT,
        (
            "puedes hacer graficas",
            "puedes generar graficas",
            "puedes hacer dashboards",
            "puedes generar reportes",
            "puedes exportar informacion",
            "puedes exportar a excel",
            "puedes comparar meses",
            "puedes comparar anos",
            "puedes comparar clientes",
            "puedes analizar tendencias",
            "puedes detectar anomalias",
            "puedes encontrar riesgos",
            "puedes encontrar oportunidades",
            "puedes hacer recomendaciones",
            "puedes hacer predicciones",
            "puedes hacer forecasting",
            "puedes hacer proyecciones",
        ),
    ),
    (
        Intent.DATA_COVERAGE,
        (
            "cobertura de datos",
            "que periodo cubres",
            "que periodo manejas",
            "que rango cubres",
            "alcance de datos",
            "que datos cubres",
            "cual es la cobertura de datos",
            "hasta cuando tienes datos",
            "hasta que fecha sabes",
            "hasta que fecha estas actualizado",
            "hasta donde llegan tus datos",
            "desde cuando tienes informacion",
            "de que fecha a que fecha sabes",
            "de que fecha a que fecha tienes informacion",
            "que anos tienes",
        ),
    ),
]

EXECUTIVE_INTENT_PATTERNS: list[tuple[Intent, tuple[str, ...]]] = [
    (
        Intent.BUSINESS_CONCENTRATION,
        (
            "donde esta concentrado el negocio",
            "concentrado el negocio",
            "dependemos de pocos clientes",
            "que tan concentrada esta la operacion",
            "concentracion del negocio",
            "concentracion de la operacion",
            "donde esta el negocio",
            "donde se concentra el negocio",
            "donde esta la mayor actividad",
            "donde esta la mayor concentracion",
            "quien mueve mas dinero",
        ),
    ),
    (
        Intent.EXECUTIVE_INSIGHTS,
        (
            "que hallazgos detectaste",
            "que hallazgos encontraste",
            "que hallazgos relevantes",
            "que hallazgos",
            "que conclusiones tienes",
            "que conclusiones",
            "que insights relevantes existen",
            "insights relevantes existen",
            "que encontraste raro",
            "que viste interesante",
            "que descubriste",
            "que detectaste",
            "que insights tienes",
        ),
    ),
    (
        Intent.YEAR_SUMMARY,
        (
            "resumen ejecutivo del ano",
            "resumen ejecutivo del anio",
            "resumen del ejercicio",
            "como estuvo el ejercicio",
            "resume el ejercicio",
            "resume 2025",
            "resume el ano 2025",
            "resume el anio 2025",
        ),
    ),
    (
        Intent.MONTH_ANALYSIS,
        (
            "que paso en",
            "que ocurrio en",
            "analiza",
            "resumen de enero",
            "resumen de febrero",
            "resumen de marzo",
            "resumen de abril",
            "resumen de mayo",
            "resumen de junio",
            "resumen de julio",
            "resumen de agosto",
            "resumen de septiembre",
            "resumen de octubre",
            "resumen de noviembre",
            "resumen de diciembre",
        ),
    ),
]

MONTH_ANALYSIS_VERBS = ("que paso en", "que ocurrio en", "analiza", "resumen de", "resume")
MONTH_NAMES = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
)

MATCH_CONFIDENCE: dict[str, float] = {
    "exact": 1.0,
    "synonym": 0.94,
    "spelling": 0.90,
    "partial": 0.80,
    "none": 0.0,
}

BUSINESS_INTENT_PATTERNS: list[tuple[Intent, tuple[str, ...]]] = [
    (
        Intent.RISKS,
        (
            "que te preocupa",
            "que riesgos detectas",
            "que riesgos ves",
            "donde ves riesgos",
            "que podria salir mal",
            "que podria fallar",
        ),
    ),
    (
        Intent.OPPORTUNITIES,
        (
            "que oportunidades detectas",
            "que oportunidades observas",
            "que oportunidades ves",
            "donde hay oportunidad",
            "donde podemos crecer",
            "que hallazgos positivos encontraste",
            "que hallazgos positivos",
        ),
    ),
    (
        Intent.EXECUTIVE_SUMMARY,
        (
            "haz un resumen ejecutivo",
            "resumen ejecutivo del",
            "resumen ejecutivo de",
            "resumen del ano",
            "resumen del anio",
            "resumen del ejercicio",
            "que paso en 2025",
            "que paso en 2024",
            "que paso en 2023",
            "dame un resumen general",
            "resumen empresarial",
            "resumen ejecutivo",
        ),
    ),
    (
        Intent.CLIENTE_CRECIMIENTO,
        (
            "que cliente crecio mas",
            "que cliente crecio",
            "cliente que mas crecio",
            "cliente con mayor crecimiento",
            "quien esta creciendo mas",
            "cliente con mas crecimiento",
        ),
    ),
    (
        Intent.CLIENTE_CAIDA,
        (
            "que cliente cayo mas",
            "cliente que mas cayo",
            "cliente con menor crecimiento",
            "cliente en declive",
            "cliente que menos crece",
        ),
    ),
    (
        Intent.PROVEEDOR_CRECIMIENTO,
        (
            "que proveedor crecio mas",
            "proveedor que mas crecio",
            "proveedor con mayor crecimiento",
            "proveedor con mas crecimiento",
        ),
    ),
    (
        Intent.PROVEEDOR_CAIDA,
        (
            "que proveedor cayo mas",
            "proveedor que mas cayo",
            "proveedor en declive",
            "proveedor que menos crece",
        ),
    ),
    (
        Intent.WORST_MONTH,
        (
            "cual fue el peor mes",
            "cual es el peor mes",
            "peor mes",
            "mes mas debil",
            "mes con menor actividad",
            "mes mas bajo",
        ),
    ),
    (
        Intent.BEST_MONTH,
        (
            "cual fue el mejor mes",
            "cual es el mejor mes",
            "mejor mes",
            "mes mas fuerte",
            "mes con mejor desempeno",
            "mes mas activo",
        ),
    ),
    (
        Intent.BOTTOM_CLIENTES,
        (
            "cual es nuestro peor cliente",
            "cual es el peor cliente",
            "quien es nuestro peor cliente",
            "peor cliente",
            "cliente menos importante",
            "cliente con menos actividad",
            "cliente que menos compra",
            "quien nos compra menos",
            "quien aporta menos",
            "cliente mas pequeno",
        ),
    ),
    (
        Intent.BOTTOM_PROVEEDORES,
        (
            "peor proveedor",
            "proveedor menos activo",
            "proveedor mas pequeno",
            "quien nos vende menos",
            "cual es el peor proveedor",
        ),
    ),
    (
        Intent.BOTTOM_CUENTAS,
        (
            "cuenta menos utilizada",
            "cuenta con menor actividad",
            "cuenta menos usada",
            "peor cuenta",
            "cual es la peor cuenta",
        ),
    ),
]


class IntentRouter:
    def route(
        self,
        question: str,
        *,
        corrections_applied: list[str] | None = None,
        intent_hint: str | None = None,
    ) -> IntentMatch:
        normalized = self._normalize(question)
        if not normalized:
            return IntentMatch(Intent.UNKNOWN, 0.0, match_type="none")

        corrections = corrections_applied or []

        evolution = self._match_evolution(normalized)
        if evolution is not None:
            intent, entity_code = evolution
            match = self._finalize(intent, "exact", corrections, intent_hint)
            if entity_code:
                return IntentMatch(
                    match.intent,
                    match.confidence,
                    entity_code=entity_code,
                    match_type=match.match_type,
                )
            return match

        executive = self._match_executive(normalized)
        if executive is not None:
            return self._finalize(executive, "exact", corrections, intent_hint)

        business = self._match_business_intents(normalized)
        if business is not None:
            intent, match_type = business
            return self._finalize(intent, match_type, corrections, intent_hint)

        human = self._match_human_intents(normalized)
        if human is not None:
            return self._finalize(human, "exact", corrections, intent_hint)

        for intent, phrases in INTENT_PATTERNS:
            if any(phrase in normalized for phrase in phrases):
                return self._finalize(intent, "exact", corrections, intent_hint)

        if self._matches_resumen_mensual(normalized):
            return self._finalize(Intent.RESUMEN_MENSUAL, "partial", corrections, intent_hint)

        return IntentMatch(Intent.UNKNOWN, 0.0, match_type="none")

    def _finalize(
        self,
        intent: Intent,
        match_type: str,
        corrections: list[str],
        intent_hint: str | None,
    ) -> IntentMatch:
        confidence = self._compute_confidence(intent, match_type, corrections, intent_hint)
        resolved_type = match_type
        if intent_hint and intent_hint == intent.value:
            resolved_type = "synonym"
        elif corrections:
            resolved_type = "spelling"
        return IntentMatch(intent, confidence, match_type=resolved_type)

    @staticmethod
    def _compute_confidence(
        intent: Intent,
        match_type: str,
        corrections: list[str],
        intent_hint: str | None,
    ) -> float:
        if intent == Intent.UNKNOWN:
            return 0.0
        if intent_hint and intent_hint == intent.value:
            return MATCH_CONFIDENCE["synonym"]
        if corrections:
            return MATCH_CONFIDENCE["spelling"]
        return MATCH_CONFIDENCE.get(match_type, MATCH_CONFIDENCE["partial"])

    def _match_executive(self, normalized: str) -> Intent | None:
        if re.search(r"\bresume\s+20\d{2}\b", normalized):
            return Intent.YEAR_SUMMARY

        for intent, phrases in EXECUTIVE_INTENT_PATTERNS:
            if any(phrase in normalized for phrase in phrases):
                if intent == Intent.MONTH_ANALYSIS and not self._contains_month(normalized):
                    continue
                return intent

        if self._contains_month(normalized) and any(
            verb in normalized for verb in MONTH_ANALYSIS_VERBS
        ):
            return Intent.MONTH_ANALYSIS

        return None

    def _match_business_intents(self, normalized: str) -> tuple[Intent, str] | None:
        if re.search(r"\bque paso en 20\d{2}\b", normalized):
            return Intent.EXECUTIVE_SUMMARY, "exact"

        for intent, phrases in BUSINESS_INTENT_PATTERNS:
            for phrase in phrases:
                if normalized == phrase or normalized.startswith(f"{phrase} "):
                    return intent, "exact"
                if phrase in normalized:
                    return intent, "partial"
        return None

    def _match_human_intents(self, normalized: str) -> Intent | None:
        for intent, phrases in HUMAN_INTENT_PATTERNS:
            if any(phrase in normalized for phrase in phrases):
                return intent
        return None

    @staticmethod
    def _contains_month(normalized: str) -> bool:
        return any(re.search(rf"\b{month}\b", normalized) for month in MONTH_NAMES)

    @staticmethod
    def _normalize(text: str) -> str:
        lowered = text.lower().strip()
        decomposed = unicodedata.normalize("NFD", lowered)
        without_accents = "".join(
            char for char in decomposed if unicodedata.category(char) != "Mn"
        )
        cleaned = re.sub(r"[^\w\s]", " ", without_accents)
        return re.sub(r"\s+", " ", cleaned).strip()

    @staticmethod
    def _matches_resumen_mensual(normalized: str) -> bool:
        if "resumen" in normalized and any(word in normalized for word in ("mes", "meses")):
            return True
        return any(keyword in normalized for keyword in RESUMEN_MENSUAL_KEYWORDS)

    def _match_evolution(self, normalized: str) -> tuple[Intent, str | None] | None:
        if re.search(
            r"evolucion.*cliente|cliente.*evolucion|historico.*cliente|historial.*cliente",
            normalized,
        ):
            code = self._extract_cliente_code(normalized)
            if code:
                return Intent.EVOLUCION_CLIENTE, code
            return None

        if re.search(
            r"evolucion.*proveedor|proveedor.*evolucion|historico.*proveedor|historial.*proveedor",
            normalized,
        ):
            code = self._extract_numeric_code(normalized)
            if code:
                return Intent.EVOLUCION_PROVEEDOR, code
            return None

        if re.search(
            r"evolucion.*cuenta|cuenta.*evolucion|historico.*cuenta|historial.*cuenta",
            normalized,
        ):
            code = self._extract_numeric_code(normalized)
            if code:
                return Intent.EVOLUCION_CUENTA, code
            return None

        return None

    @staticmethod
    def _extract_cliente_code(normalized: str) -> str | None:
        match = re.search(r"\b(c\d+)\b", normalized)
        if match:
            return match.group(1).upper()
        return None

    @staticmethod
    def _extract_numeric_code(normalized: str) -> str | None:
        match = re.search(r"\b(\d{5,})\b", normalized)
        if match:
            return match.group(1)
        return None
