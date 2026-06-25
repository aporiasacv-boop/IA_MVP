import json
from typing import Any

from app.services.intent_router import Intent


class PromptBuilder:
    SYSTEM_RULES = (
        "Eres un analista empresarial senior. "
        "Redacta respuestas ejecutivas breves en espanol."
    )

    STRICT_RULES = (
        "REGLAS ESTRICTAS:\n"
        "- Usa EXCLUSIVAMENTE los datos proporcionados.\n"
        "- NO generes SQL.\n"
        "- NO inventes cifras, nombres, fechas ni conclusiones.\n"
        "- NO consultes bases de datos ni supongas informacion adicional.\n"
        "- Si los datos son insuficientes, indicalo claramente.\n"
        "- Maximo 4 oraciones.\n"
        "- Tono profesional y directo.\n"
        "- Cuando sea relevante, indica explicitamente el periodo analizado."
    )

    INTENT_LABELS = {
        Intent.TOP_CLIENTES.value: "Ranking de clientes principales",
        Intent.TOP_PROVEEDORES.value: "Ranking de proveedores principales",
        Intent.TOP_CUENTAS.value: "Ranking de cuentas contables principales",
        Intent.RESUMEN_MENSUAL.value: "Resumen mensual de actividad",
        Intent.KPIS.value: "Indicadores clave generales",
        Intent.KPIS_EJECUTIVOS.value: "Indicadores ejecutivos consolidados",
        Intent.INSIGHTS.value: "Insights empresariales detectados",
        Intent.EVOLUCION_CLIENTE.value: "Evolucion mensual de cliente",
        Intent.EVOLUCION_PROVEEDOR.value: "Evolucion mensual de proveedor",
        Intent.EVOLUCION_CUENTA.value: "Evolucion mensual de cuenta",
        Intent.UNKNOWN.value: "Consulta no reconocida",
        Intent.MONTH_ANALYSIS.value: "Analisis ejecutivo mensual consolidado",
        Intent.YEAR_SUMMARY.value: "Resumen ejecutivo anual consolidado",
        Intent.EXECUTIVE_INSIGHTS.value: "Hallazgos y conclusiones ejecutivas",
        Intent.BUSINESS_CONCENTRATION.value: "Analisis de concentracion del negocio",
        Intent.KNOWLEDGE_SCOPE.value: "Alcance de conocimiento disponible",
        Intent.DATA_COVERAGE.value: "Cobertura temporal y volumetrica del dataset",
        Intent.CAPABILITIES.value: "Capacidades analiticas del asistente",
    }

    EXECUTIVE_INTENTS = frozenset({
        Intent.MONTH_ANALYSIS.value,
        Intent.YEAR_SUMMARY.value,
        Intent.EXECUTIVE_INSIGHTS.value,
        Intent.BUSINESS_CONCENTRATION.value,
    })

    EXECUTIVE_RULES = (
        "INSTRUCCIONES EJECUTIVAS:\n"
        "- Integra las fuentes del contexto en una narrativa breve y clara.\n"
        "- Indica explicitamente el periodo analizado al inicio.\n"
        "- Prioriza hallazgos, concentracion, picos y entidades principales.\n"
        "- Maximo 5 oraciones.\n"
        "- No repitas el JSON; sintetiza para un director general."
    )

    def build(
        self,
        question: str,
        intent: str,
        data: Any,
        dataset_context: str | None = None,
        temporal_context: str | None = None,
        sources: list[str] | None = None,
    ) -> tuple[str, int]:
        intent_label = self.INTENT_LABELS.get(intent, intent)
        data_json = json.dumps(data, ensure_ascii=False, indent=2, default=str)
        context_block = ""
        if dataset_context:
            context_block += f"\n{dataset_context}\n"
        if temporal_context:
            context_block += f"{temporal_context}\n"
        if sources:
            context_block += f"Fuentes consolidadas: {', '.join(sources)}\n"
        context_chars = len(context_block) + len(data_json)
        rules = self.STRICT_RULES
        if intent in self.EXECUTIVE_INTENTS:
            rules = f"{self.STRICT_RULES}\n\n{self.EXECUTIVE_RULES}"
        prompt = (
            f"{self.SYSTEM_RULES}\n\n"
            f"{rules}\n\n"
            f"{context_block}"
            f"Pregunta del usuario:\n{question.strip()}\n\n"
            f"Intencion detectada: {intent}\n"
            f"Contexto analitico: {intent_label}\n\n"
            f"Datos verificados (JSON):\n{data_json}\n\n"
            f"Redacta una respuesta ejecutiva breve basada exclusivamente "
            f"en los siguientes datos:\n"
        )
        return prompt, context_chars
