from dataclasses import dataclass
from datetime import date
from typing import Any

from pydantic import BaseModel

import time

from app.services.analytics_service import AnalyticsService
from app.services.insights_engine import InsightsEngine
from app.services.intent_router import Intent
from app.services.metadata_service import MetadataService
from app.services.temporal_resolver import TemporalResolver
from app.services.timing_collector import TimingCollector, elapsed_ms

MESES = {
    1: "enero",
    2: "febrero",
    3: "marzo",
    4: "abril",
    5: "mayo",
    6: "junio",
    7: "julio",
    8: "agosto",
    9: "septiembre",
    10: "octubre",
    11: "noviembre",
    12: "diciembre",
}


@dataclass(frozen=True)
class ExecutiveContext:
    sources: list[str]
    temporal: dict[str, str] | None
    data: dict[str, Any]


class BusinessContextBuilder:
    EXECUTIVE_INTENTS = frozenset({
        Intent.MONTH_ANALYSIS,
        Intent.YEAR_SUMMARY,
        Intent.EXECUTIVE_INSIGHTS,
        Intent.BUSINESS_CONCENTRATION,
    })

    def __init__(
        self,
        analytics_service: AnalyticsService,
        insights_engine: InsightsEngine,
        metadata_service: MetadataService,
    ) -> None:
        self.analytics_service = analytics_service
        self.insights_engine = insights_engine
        self.metadata_service = metadata_service

    def is_executive(self, intent: Intent) -> bool:
        return intent in self.EXECUTIVE_INTENTS

    def build(
        self,
        intent: Intent,
        question: str,
        timings: TimingCollector | None = None,
    ) -> ExecutiveContext:
        started = time.perf_counter()
        builders = {
            Intent.MONTH_ANALYSIS: self._build_month_analysis,
            Intent.YEAR_SUMMARY: self._build_year_summary,
            Intent.EXECUTIVE_INSIGHTS: self._build_executive_insights,
            Intent.BUSINESS_CONCENTRATION: self._build_business_concentration,
        }
        builder = builders[intent]
        result = builder(question)
        if timings is not None:
            timings.context_ms = elapsed_ms(started)
        return result

    def _build_month_analysis(self, question: str) -> ExecutiveContext:
        metadata = self.metadata_service.get_dataset_summary()
        resolver = TemporalResolver.from_metadata(metadata)
        temporal = resolver.resolve_from_question(question)
        if temporal is None:
            temporal = {
                "inicio": metadata["fecha_minima"],
                "fin": metadata["fecha_maxima"],
            }

        mes_info = self._extract_month_from_period(temporal)
        resumen = self._serialize(self.analytics_service.get_resumen_mensual())
        mes_data = self._filter_month_resumen(resumen, mes_info)
        promedio = self._monthly_average(resumen)
        kpis = self._serialize(self.analytics_service.get_kpis_ejecutivos())
        insights = self._serialize(self.insights_engine.generate_insights())
        relevant_insights = self._filter_insights_for_month(insights, mes_info)

        return ExecutiveContext(
            sources=["METADATA", "RESUMEN_MENSUAL", "KPIS_EJECUTIVOS", "INSIGHTS"],
            temporal=temporal,
            data={
                "metadata": metadata,
                "temporal": temporal,
                "mes": mes_data,
                "promedio_mensual": promedio,
                "kpis_ejecutivos": kpis,
                "insights": relevant_insights,
            },
        )

    def _build_year_summary(self, question: str) -> ExecutiveContext:
        metadata = self.metadata_service.get_dataset_summary()
        resolver = TemporalResolver.from_metadata(metadata)
        temporal = resolver.resolve_from_question(question) or {
            "inicio": metadata["fecha_minima"],
            "fin": metadata["fecha_maxima"],
        }

        return ExecutiveContext(
            sources=[
                "METADATA",
                "KPIS_EJECUTIVOS",
                "INSIGHTS",
                "TOP_CLIENTES",
                "TOP_PROVEEDORES",
            ],
            temporal=temporal,
            data={
                "metadata": metadata,
                "temporal": temporal,
                "kpis_ejecutivos": self._serialize(
                    self.analytics_service.get_kpis_ejecutivos()
                ),
                "insights": self._serialize(self.insights_engine.generate_insights()),
                "top_clientes": self._serialize(
                    self.analytics_service.get_top_clientes(5)
                ),
                "top_proveedores": self._serialize(
                    self.analytics_service.get_top_proveedores(5)
                ),
            },
        )

    def _build_executive_insights(self, _question: str) -> ExecutiveContext:
        metadata = self.metadata_service.get_dataset_summary()
        temporal = {
            "inicio": metadata["fecha_minima"],
            "fin": metadata["fecha_maxima"],
        }
        return ExecutiveContext(
            sources=["INSIGHTS", "KPIS_EJECUTIVOS", "METADATA"],
            temporal=temporal,
            data={
                "metadata": metadata,
                "temporal": temporal,
                "insights": self._serialize(self.insights_engine.generate_insights()),
                "kpis_ejecutivos": self._serialize(
                    self.analytics_service.get_kpis_ejecutivos()
                ),
            },
        )

    def _build_business_concentration(self, _question: str) -> ExecutiveContext:
        metadata = self.metadata_service.get_dataset_summary()
        temporal = {
            "inicio": metadata["fecha_minima"],
            "fin": metadata["fecha_maxima"],
        }
        insights = self._serialize(self.insights_engine.generate_insights())
        concentration_insights = [
            item
            for item in insights
            if isinstance(item, dict)
            and (
                "concentracion" in str(item.get("tipo", ""))
                or "dominante" in str(item.get("tipo", ""))
            )
        ]
        if not concentration_insights:
            concentration_insights = insights[:5]

        return ExecutiveContext(
            sources=["INSIGHTS", "TOP_CLIENTES", "KPIS_EJECUTIVOS", "METADATA"],
            temporal=temporal,
            data={
                "metadata": metadata,
                "temporal": temporal,
                "insights": concentration_insights,
                "top_clientes": self._serialize(
                    self.analytics_service.get_top_clientes(10)
                ),
                "kpis_ejecutivos": self._serialize(
                    self.analytics_service.get_kpis_ejecutivos()
                ),
            },
        )

    @staticmethod
    def _extract_month_from_period(period: dict[str, str]) -> tuple[int, int]:
        start = date.fromisoformat(period["inicio"])
        return start.year, start.month

    @staticmethod
    def _filter_month_resumen(
        resumen: list[dict[str, Any]],
        mes_info: tuple[int, int],
    ) -> dict[str, Any] | None:
        anio, mes = mes_info
        for row in resumen:
            if int(row.get("anio", 0)) == anio and int(row.get("mes", 0)) == mes:
                return row
        return None

    @staticmethod
    def _monthly_average(resumen: list[dict[str, Any]]) -> dict[str, Any]:
        if not resumen:
            return {"movimientos": 0, "monto_total": "0"}
        total_mov = sum(int(row.get("movimientos", 0)) for row in resumen)
        total_monto = sum(float(row.get("monto_total", 0)) for row in resumen)
        count = len(resumen)
        return {
            "movimientos": round(total_mov / count, 2),
            "monto_total": round(total_monto / count, 2),
            "meses_analizados": count,
        }

    @staticmethod
    def _filter_insights_for_month(
        insights: list[dict[str, Any]],
        mes_info: tuple[int, int],
    ) -> list[dict[str, Any]]:
        anio, mes = mes_info
        month_name = MESES.get(mes, str(mes))
        filtered = []
        for item in insights:
            if not isinstance(item, dict):
                continue
            mensaje = str(item.get("mensaje", "")).lower()
            tipo = str(item.get("tipo", "")).lower()
            if month_name in mensaje:
                filtered.append(item)
                continue
            if tipo in {"mes_pico_actividad", "mes_pico_volumen", "mes_atipico"}:
                filtered.append(item)
                continue
            if str(anio) in mensaje and month_name in mensaje:
                filtered.append(item)
        return filtered or insights[:4]

    @staticmethod
    def _serialize(value: Any) -> Any:
        if isinstance(value, BaseModel):
            return value.model_dump(mode="json")
        if isinstance(value, list):
            return [BusinessContextBuilder._serialize(item) for item in value]
        if isinstance(value, dict):
            return {
                key: BusinessContextBuilder._serialize(item)
                for key, item in value.items()
            }
        return value
