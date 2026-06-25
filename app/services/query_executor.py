from typing import Any

import time

from pydantic import BaseModel

from app.services.analytics_service import AnalyticsService
from app.services.insights_engine import InsightsEngine
from app.services.intent_router import Intent, IntentMatch
from app.services.metadata_service import MetadataService
from app.services.timing_collector import TimingCollector, elapsed_ms


DEFAULT_TOP_LIMIT = 10


class QueryExecutor:
    KNOWLEDGE_TOPICS = (
        "Clientes",
        "Proveedores",
        "KPIs",
        "Tendencias",
        "Insights",
        "Resúmenes ejecutivos",
    )

    CAPABILITIES = (
        "Consultar ranking de clientes y proveedores",
        "Revisar KPIs y resúmenes mensuales",
        "Analizar tendencias y evolución por entidad",
        "Obtener insights y narrativas ejecutivas",
        "Analizar periodos específicos (mes o año)",
    )

    def __init__(
        self,
        analytics_service: AnalyticsService,
        insights_engine: InsightsEngine,
        metadata_service: MetadataService | None = None,
    ) -> None:
        self.analytics_service = analytics_service
        self.insights_engine = insights_engine
        self.metadata_service = metadata_service

    def execute(
        self,
        match: IntentMatch,
        timings: TimingCollector | None = None,
    ) -> Any:
        started = time.perf_counter()
        handlers = {
            Intent.TOP_CLIENTES: self._top_clientes,
            Intent.TOP_PROVEEDORES: self._top_proveedores,
            Intent.TOP_CUENTAS: self._top_cuentas,
            Intent.RESUMEN_MENSUAL: self._resumen_mensual,
            Intent.KPIS: self._kpis,
            Intent.KPIS_EJECUTIVOS: self._kpis_ejecutivos,
            Intent.INSIGHTS: self._insights,
            Intent.EVOLUCION_CLIENTE: self._evolucion_cliente,
            Intent.EVOLUCION_PROVEEDOR: self._evolucion_proveedor,
            Intent.EVOLUCION_CUENTA: self._evolucion_cuenta,
            Intent.KNOWLEDGE_SCOPE: self._knowledge_scope,
            Intent.DATA_COVERAGE: self._data_coverage,
            Intent.CAPABILITIES: self._capabilities,
            Intent.UNKNOWN: self._unknown,
        }
        handler = handlers.get(match.intent, self._unknown)
        result = handler(match)
        if timings is not None:
            timings.query_ms = elapsed_ms(started)
        return result

    def _top_clientes(self, _match: IntentMatch) -> list[dict[str, Any]]:
        return self._serialize(self.analytics_service.get_top_clientes(DEFAULT_TOP_LIMIT))

    def _top_proveedores(self, _match: IntentMatch) -> list[dict[str, Any]]:
        return self._serialize(self.analytics_service.get_top_proveedores(DEFAULT_TOP_LIMIT))

    def _top_cuentas(self, _match: IntentMatch) -> list[dict[str, Any]]:
        return self._serialize(self.analytics_service.get_top_cuentas(DEFAULT_TOP_LIMIT))

    def _resumen_mensual(self, _match: IntentMatch) -> list[dict[str, Any]]:
        return self._serialize(self.analytics_service.get_resumen_mensual())

    def _kpis(self, _match: IntentMatch) -> dict[str, Any]:
        return self._serialize(self.analytics_service.get_kpis())

    def _kpis_ejecutivos(self, _match: IntentMatch) -> dict[str, Any]:
        return self._serialize(self.analytics_service.get_kpis_ejecutivos())

    def _insights(self, _match: IntentMatch) -> list[dict[str, Any]]:
        return self._serialize(self.insights_engine.generate_insights())

    def _evolucion_cliente(self, match: IntentMatch) -> list[dict[str, Any]]:
        if not match.entity_code:
            return []
        return self._serialize(
            self.analytics_service.get_evolucion_cliente(match.entity_code)
        )

    def _evolucion_proveedor(self, match: IntentMatch) -> list[dict[str, Any]]:
        if not match.entity_code:
            return []
        return self._serialize(
            self.analytics_service.get_evolucion_proveedor(match.entity_code)
        )

    def _evolucion_cuenta(self, match: IntentMatch) -> list[dict[str, Any]]:
        if not match.entity_code:
            return []
        return self._serialize(
            self.analytics_service.get_evolucion_cuenta(match.entity_code)
        )

    def _knowledge_scope(self, _match: IntentMatch) -> dict[str, Any]:
        return {
            "topics": list(self.KNOWLEDGE_TOPICS),
            "metadata": self._metadata_summary(),
        }

    def _data_coverage(self, _match: IntentMatch) -> dict[str, Any]:
        return {"coverage": self._metadata_summary()}

    def _capabilities(self, _match: IntentMatch) -> dict[str, Any]:
        return {
            "capabilities": list(self.CAPABILITIES),
            "metadata": self._metadata_summary(),
        }

    def _metadata_summary(self) -> dict[str, Any] | None:
        if self.metadata_service is None:
            return None
        return self.metadata_service.get_dataset_summary()

    @staticmethod
    def _unknown(_match: IntentMatch) -> None:
        return None

    @staticmethod
    def _serialize(value: Any) -> Any:
        if isinstance(value, BaseModel):
            return value.model_dump(mode="json")
        if isinstance(value, list):
            return [QueryExecutor._serialize(item) for item in value]
        if isinstance(value, dict):
            return {key: QueryExecutor._serialize(item) for key, item in value.items()}
        return value
