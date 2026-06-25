from typing import Any

import time

from app.schemas.prompt_metrics import PromptMetrics
from app.services.intent_router import Intent
from app.services.llm_context_optimizer import LlmContextOptimizer
from app.services.metadata_service import MetadataService
from app.services.ollama_client import OllamaClient, OllamaError
from app.services.prompt_audit import PromptAudit
from app.services.prompt_builder import PromptBuilder
from app.services.temporal_resolver import TemporalResolver
from app.services.timing_collector import TimingCollector, elapsed_ms

MESES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}


class ResponseGenerator:
    FALLBACK_PREFIX = (
        "No fue posible contactar al modelo. Resultado estructurado disponible."
    )

    DETERMINISTIC_INTENTS = frozenset({
        Intent.KNOWLEDGE_SCOPE.value,
        Intent.DATA_COVERAGE.value,
        Intent.CAPABILITIES.value,
    })

    def __init__(
        self,
        ollama_client: OllamaClient | None = None,
        prompt_builder: PromptBuilder | None = None,
        metadata_service: MetadataService | None = None,
    ) -> None:
        self.ollama_client = ollama_client or OllamaClient()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.metadata_service = metadata_service
        self.context_optimizer = LlmContextOptimizer()

    def generate(
        self,
        question: str,
        intent: str,
        data: Any,
        intent_confidence: float = 1.0,
        sources: list[str] | None = None,
        timings: TimingCollector | None = None,
    ) -> tuple[str, PromptMetrics]:
        if intent_confidence < 0.60 or intent == Intent.UNKNOWN.value or data is None:
            return self._low_confidence_answer(), PromptMetrics()

        if intent in self.DETERMINISTIC_INTENTS:
            summary = self._deterministic_summary(intent, data)
            return summary or self._low_confidence_answer(), PromptMetrics()

        metadata_summary = None
        if self.metadata_service is not None:
            metadata_summary = self.metadata_service.get_dataset_summary()

        llm_data, sources_used = self.context_optimizer.optimize(
            intent,
            data,
            metadata=metadata_summary,
        )
        temporal_context = self._build_temporal_context(question, data)
        dataset_context = None

        prompt_started = time.perf_counter()
        prompt, context_chars = self.prompt_builder.build(
            question,
            intent,
            llm_data,
            dataset_context=dataset_context,
            temporal_context=temporal_context,
            sources=sources_used or sources,
        )
        if timings is not None:
            timings.prompt_ms = elapsed_ms(prompt_started)

        llm_started = time.perf_counter()
        try:
            answer = self.ollama_client.generate(prompt)
        except OllamaError:
            answer = self._fallback_answer(intent, data, temporal_context)
        finally:
            if timings is not None:
                timings.llm_ms = elapsed_ms(llm_started)

        audit = PromptAudit.analyze(
            question=question,
            prompt=prompt,
            context_chars=context_chars,
            sources_used=sources_used or sources or [],
            answer=answer,
        )
        return answer, audit.metrics

    def _build_temporal_context(
        self,
        question: str,
        data: Any,
    ) -> str | None:
        if isinstance(data, dict) and data.get("temporal"):
            temporal = data["temporal"]
            return (
                f"Referencia temporal resuelta: {temporal['inicio']} a {temporal['fin']}."
            )
        if self.metadata_service is not None:
            summary = self.metadata_service.get_dataset_summary()
            resolver = TemporalResolver.from_metadata(summary)
            period = resolver.resolve_from_question(question)
            return resolver.format_context(period)
        return None

    def _low_confidence_answer(self) -> str:
        return (
            "No entendí completamente tu consulta.\n\n"
            "¿Te refieres a:\n\n"
            "• Clientes\n"
            "• Proveedores\n"
            "• KPIs\n"
            "• Cobertura de datos\n"
            "• Hallazgos empresariales\n\n"
            "Intenta escribir la consulta de otra manera."
        )

    def _unknown_answer(self) -> str:
        return self._low_confidence_answer()

    def _fallback_answer(
        self,
        intent: str,
        data: Any,
        temporal_context: str | None = None,
    ) -> str:
        summary = self._deterministic_summary(intent, data)
        period_note = ""
        if temporal_context:
            period_note = f" {temporal_context}"
        if summary:
            return f"{self.FALLBACK_PREFIX} {summary}{period_note}"
        return f"{self.FALLBACK_PREFIX}{period_note}"

    def _deterministic_summary(self, intent: str, data: Any) -> str:
        handlers = {
            Intent.TOP_CLIENTES.value: self._summary_top_clientes,
            Intent.TOP_PROVEEDORES.value: self._summary_top_proveedores,
            Intent.TOP_CUENTAS.value: self._summary_top_cuentas,
            Intent.RESUMEN_MENSUAL.value: self._summary_resumen_mensual,
            Intent.KPIS.value: self._summary_kpis,
            Intent.KPIS_EJECUTIVOS.value: self._summary_kpis_ejecutivos,
            Intent.INSIGHTS.value: self._summary_insights,
            Intent.EVOLUCION_CLIENTE.value: self._summary_evolucion_cliente,
            Intent.EVOLUCION_PROVEEDOR.value: self._summary_evolucion_proveedor,
            Intent.EVOLUCION_CUENTA.value: self._summary_evolucion_cuenta,
            Intent.MONTH_ANALYSIS.value: self._summary_executive,
            Intent.YEAR_SUMMARY.value: self._summary_executive,
            Intent.EXECUTIVE_INSIGHTS.value: self._summary_executive,
            Intent.BUSINESS_CONCENTRATION.value: self._summary_executive,
            Intent.KNOWLEDGE_SCOPE.value: self._summary_knowledge_scope,
            Intent.DATA_COVERAGE.value: self._summary_data_coverage,
            Intent.CAPABILITIES.value: self._summary_capabilities,
        }
        handler = handlers.get(intent)
        if handler is None:
            return ""
        return handler(data)

    @staticmethod
    def _first_item(data: Any) -> dict[str, Any] | None:
        if isinstance(data, list) and data:
            item = data[0]
            if isinstance(item, dict):
                return item
        return None

    def _summary_top_clientes(self, data: Any) -> str:
        item = self._first_item(data)
        if not item:
            return "No hay clientes disponibles en el resultado."
        return (
            f"El cliente con mayor actividad es {item.get('cliente_nombre')} "
            f"({item.get('cliente_codigo')}) con {item.get('movimientos')} movimientos."
        )

    def _summary_top_proveedores(self, data: Any) -> str:
        item = self._first_item(data)
        if not item:
            return "No hay proveedores disponibles en el resultado."
        return (
            f"El proveedor principal es {item.get('proveedor_nombre')} "
            f"({item.get('proveedor_codigo')}) con {item.get('movimientos')} movimientos."
        )

    def _summary_top_cuentas(self, data: Any) -> str:
        item = self._first_item(data)
        if not item:
            return "No hay cuentas disponibles en el resultado."
        return (
            f"La cuenta con mayor actividad es {item.get('cuenta_nombre')} "
            f"({item.get('cuenta_codigo')}) con {item.get('movimientos')} movimientos."
        )

    def _summary_resumen_mensual(self, data: Any) -> str:
        if not isinstance(data, list) or not data:
            return "No hay resumen mensual disponible."
        peak = max(data, key=lambda row: row.get("movimientos", 0))
        mes = MESES.get(int(peak.get("mes", 0)), str(peak.get("mes")))
        return (
            f"El ejercicio registra {len(data)} meses analizados. "
            f"El mes de mayor actividad fue {mes} de {peak.get('anio')} "
            f"con {peak.get('movimientos')} movimientos."
        )

    def _summary_kpis(self, data: Any) -> str:
        if not isinstance(data, dict):
            return ""
        return (
            f"El datamart registra {data.get('movimientos')} movimientos, "
            f"{data.get('clientes')} clientes, {data.get('proveedores')} proveedores "
            f"y {data.get('cuentas')} cuentas."
        )

    def _summary_kpis_ejecutivos(self, data: Any) -> str:
        if not isinstance(data, dict):
            return ""
        cliente = data.get("cliente_principal") or {}
        mes = data.get("mes_mayor_actividad") or {}
        nombre_mes = MESES.get(int(mes.get("mes", 0)), str(mes.get("mes")))
        return (
            f"El cliente principal es {cliente.get('nombre')} con "
            f"{cliente.get('movimientos')} movimientos. "
            f"El mes pico de actividad fue {nombre_mes} con {mes.get('movimientos')} movimientos."
        )

    def _summary_insights(self, data: Any) -> str:
        if not isinstance(data, list) or not data:
            return "No hay insights disponibles."
        mensajes = [str(item.get("mensaje", "")) for item in data[:3] if isinstance(item, dict)]
        if not mensajes:
            return f"Se detectaron {len(data)} insights empresariales."
        joined = " ".join(mensajes)
        return f"Insights principales: {joined}"

    def _summary_evolucion_cliente(self, data: Any) -> str:
        item = self._first_item(data)
        if not item:
            return "No hay evolucion disponible para el cliente solicitado."
        mes = MESES.get(int(item.get("mes", 0)), str(item.get("mes")))
        return (
            f"Evolucion de {item.get('cliente_nombre')} ({item.get('cliente_codigo')}): "
            f"en {mes} de {item.get('anio')} registra {item.get('movimientos')} movimientos."
        )

    def _summary_evolucion_proveedor(self, data: Any) -> str:
        item = self._first_item(data)
        if not item:
            return "No hay evolucion disponible para el proveedor solicitado."
        mes = MESES.get(int(item.get("mes", 0)), str(item.get("mes")))
        return (
            f"Evolucion de {item.get('proveedor_nombre')} ({item.get('proveedor_codigo')}): "
            f"en {mes} de {item.get('anio')} registra {item.get('movimientos')} movimientos."
        )

    def _summary_evolucion_cuenta(self, data: Any) -> str:
        item = self._first_item(data)
        if not item:
            return "No hay evolucion disponible para la cuenta solicitada."
        mes = MESES.get(int(item.get("mes", 0)), str(item.get("mes")))
        return (
            f"Evolucion de {item.get('cuenta_nombre')} ({item.get('cuenta_codigo')}): "
            f"en {mes} de {item.get('anio')} registra {item.get('movimientos')} movimientos."
        )

    def _summary_executive(self, data: Any) -> str:
        if not isinstance(data, dict):
            return ""
        parts: list[str] = []
        temporal = data.get("temporal")
        if isinstance(temporal, dict):
            parts.append(
                f"Periodo analizado: {temporal.get('inicio')} a {temporal.get('fin')}."
            )
        mes = data.get("mes")
        if isinstance(mes, dict):
            mes_num = int(mes.get("mes", 0))
            mes_nombre = MESES.get(mes_num, str(mes.get("mes")))
            parts.append(
                f"En {mes_nombre} de {mes.get('anio')} se registraron "
                f"{mes.get('movimientos')} movimientos."
            )
        kpis = data.get("kpis_ejecutivos")
        if isinstance(kpis, dict):
            cliente = kpis.get("cliente_principal") or {}
            if cliente.get("nombre"):
                parts.append(
                    f"Cliente principal: {cliente.get('nombre')} "
                    f"({cliente.get('movimientos')} movimientos)."
                )
            participacion = kpis.get("top_5_clientes_participacion")
            if participacion is not None:
                parts.append(
                    f"Los 5 principales clientes concentran el {participacion}% del volumen."
                )
        insights = data.get("insights")
        if isinstance(insights, list) and insights:
            mensajes = [
                str(item.get("mensaje", ""))
                for item in insights[:3]
                if isinstance(item, dict) and item.get("mensaje")
            ]
            if mensajes:
                parts.append("Hallazgos: " + " ".join(mensajes))
        return " ".join(parts)

    def _summary_knowledge_scope(self, data: Any) -> str:
        if not isinstance(data, dict):
            return ""
        topics = data.get("topics") or []
        metadata = data.get("metadata") or {}
        lines = ["Tengo información verificada sobre:"]
        lines.extend(f"• {topic}" for topic in topics)
        if metadata:
            lines.append(
                f"\nCobertura del dataset: {metadata.get('fecha_minima')} a "
                f"{metadata.get('fecha_maxima')} "
                f"({metadata.get('registros', 0):,} registros)."
            )
        return "\n".join(lines)

    def _summary_data_coverage(self, data: Any) -> str:
        if not isinstance(data, dict):
            return ""
        coverage = data.get("coverage") or {}
        if not coverage:
            return "No hay metadata de cobertura disponible."
        anios = ", ".join(str(year) for year in coverage.get("anios", []))
        return (
            f"La cobertura de datos abarca del {coverage.get('fecha_minima')} "
            f"al {coverage.get('fecha_maxima')}. "
            f"Incluye {coverage.get('registros', 0):,} registros, "
            f"{coverage.get('clientes', 0)} clientes, "
            f"{coverage.get('proveedores', 0)} proveedores y "
            f"{coverage.get('cuentas', 0)} cuentas "
            f"en {coverage.get('meses', 0)} meses "
            f"({anios})."
        )

    def _summary_capabilities(self, data: Any) -> str:
        if not isinstance(data, dict):
            return ""
        capabilities = data.get("capabilities") or []
        lines = ["Puedo ayudarte con:"]
        lines.extend(f"• {item}" for item in capabilities)
        return "\n".join(lines)
