from __future__ import annotations

import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from pydantic import BaseModel
from sqlalchemy import text

from app.repositories.executive_summary_repository import ExecutiveSummaryRepository
from app.repositories.insights_repository import InsightsRepository
from app.schemas.entities import ExtractedEntities
from app.services.analytics_service import AnalyticsService
from app.services.insights_engine import InsightsEngine
from app.services.intent_router import Intent, IntentMatch
from app.services.metadata_service import MetadataService
from app.services.timing_collector import TimingCollector, elapsed_ms

DEFAULT_TOP_LIMIT = 10


@dataclass(frozen=True)
class DeterministicResponse:
    answer: str
    data: Any
    sources: list[str]


class DeterministicResponseEngine:
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

    def __init__(
        self,
        executive_summary_repository: ExecutiveSummaryRepository,
        analytics_service: AnalyticsService,
        insights_engine: InsightsEngine,
        metadata_service: MetadataService,
        insights_repository: InsightsRepository,
    ) -> None:
        self.executive_summary_repository = executive_summary_repository
        self.analytics_service = analytics_service
        self.insights_engine = insights_engine
        self.metadata_service = metadata_service
        self.insights_repository = insights_repository

    def generate(
        self,
        match: IntentMatch,
        entities: ExtractedEntities,
        timings: TimingCollector | None = None,
    ) -> DeterministicResponse:
        started = time.perf_counter()
        handlers = {
            Intent.TOP_CLIENTES: self._top_clientes,
            Intent.BOTTOM_CLIENTES: self._bottom_clientes,
            Intent.TOP_PROVEEDORES: self._top_proveedores,
            Intent.BOTTOM_PROVEEDORES: self._bottom_proveedores,
            Intent.TOP_CUENTAS: self._top_cuentas,
            Intent.BOTTOM_CUENTAS: self._bottom_cuentas,
            Intent.BEST_MONTH: self._best_month,
            Intent.WORST_MONTH: self._worst_month,
            Intent.MONTH_ANALYSIS: self._month_analysis,
            Intent.DATA_COVERAGE: self._data_coverage,
            Intent.KPIS: self._kpis,
            Intent.KPIS_EJECUTIVOS: self._kpis_ejecutivos,
            Intent.INSIGHTS: self._insights,
            Intent.CLIENTE_CRECIMIENTO: self._cliente_crecimiento,
            Intent.CLIENTE_CAIDA: self._cliente_caida,
            Intent.PROVEEDOR_CRECIMIENTO: self._proveedor_crecimiento,
            Intent.PROVEEDOR_CAIDA: self._proveedor_caida,
            Intent.RESUMEN_MENSUAL: self._resumen_mensual,
        }
        handler = handlers.get(match.intent, self._unsupported)
        result = handler(match, entities)
        if timings is not None:
            timings.deterministic_ms = elapsed_ms(started)
        return result

    def _top_clientes(self, _match: IntentMatch, _entities: ExtractedEntities) -> DeterministicResponse:
        rows = self.executive_summary_repository.obtener_top_clientes_resumen(DEFAULT_TOP_LIMIT)
        top = rows[0]
        anio = self._default_year()
        answer = (
            f"Durante {anio} el cliente con mayor actividad fue {top['cliente_nombre']} "
            f"con {top['movimientos']:,} movimientos registrados, ocupando la primera posicion "
            f"del ranking empresarial."
        )
        return DeterministicResponse(
            answer=answer,
            data=rows,
            sources=["CLIENTE_RESUMEN", "EXECUTIVE_SUMMARY"],
        )

    def _bottom_clientes(self, _match: IntentMatch, _entities: ExtractedEntities) -> DeterministicResponse:
        rows = self.executive_summary_repository.obtener_bottom_clientes_resumen(1)
        bottom = rows[0]
        answer = (
            f"El cliente con menor actividad registrada durante el periodo analizado fue "
            f"{bottom['cliente_nombre']}, con {bottom['movimientos']:,} movimientos."
        )
        return DeterministicResponse(
            answer=answer,
            data=rows,
            sources=["CLIENTE_RESUMEN", "EXECUTIVE_SUMMARY"],
        )

    def _top_proveedores(self, _match: IntentMatch, _entities: ExtractedEntities) -> DeterministicResponse:
        rows = self.executive_summary_repository.obtener_top_proveedores_resumen(DEFAULT_TOP_LIMIT)
        top = rows[0]
        anio = self._default_year()
        answer = (
            f"Durante {anio} el proveedor con mayor actividad fue {top['proveedor_nombre']} "
            f"con {top['movimientos']:,} movimientos registrados, ocupando la primera posicion "
            f"del ranking empresarial."
        )
        return DeterministicResponse(
            answer=answer,
            data=rows,
            sources=["PROVEEDOR_RESUMEN", "EXECUTIVE_SUMMARY"],
        )

    def _bottom_proveedores(self, _match: IntentMatch, _entities: ExtractedEntities) -> DeterministicResponse:
        rows = self.executive_summary_repository.obtener_bottom_proveedores_resumen(1)
        bottom = rows[0]
        answer = (
            f"El proveedor con menor actividad registrada durante el periodo analizado fue "
            f"{bottom['proveedor_nombre']}, con {bottom['movimientos']:,} movimientos."
        )
        return DeterministicResponse(
            answer=answer,
            data=rows,
            sources=["PROVEEDOR_RESUMEN", "EXECUTIVE_SUMMARY"],
        )

    def _top_cuentas(self, _match: IntentMatch, _entities: ExtractedEntities) -> DeterministicResponse:
        rows = self.executive_summary_repository.obtener_cuenta_resumen()[:DEFAULT_TOP_LIMIT]
        top = rows[0]
        anio = self._default_year()
        answer = (
            f"Durante {anio} la cuenta con mayor actividad fue {top['cuenta_nombre']} "
            f"con {top['movimientos']:,} movimientos registrados, ocupando la primera posicion "
            f"del ranking empresarial."
        )
        return DeterministicResponse(
            answer=answer,
            data=rows,
            sources=["CUENTA_RESUMEN", "EXECUTIVE_SUMMARY"],
        )

    def _bottom_cuentas(self, _match: IntentMatch, _entities: ExtractedEntities) -> DeterministicResponse:
        rows = sorted(
            self.executive_summary_repository.obtener_cuenta_resumen(),
            key=lambda row: row["ranking"],
            reverse=True,
        )[:1]
        bottom = rows[0]
        answer = (
            f"La cuenta con menor actividad registrada durante el periodo analizado fue "
            f"{bottom['cuenta_nombre']}, con {bottom['movimientos']:,} movimientos."
        )
        return DeterministicResponse(
            answer=answer,
            data=rows,
            sources=["CUENTA_RESUMEN", "EXECUTIVE_SUMMARY"],
        )

    def _best_month(self, _match: IntentMatch, _entities: ExtractedEntities) -> DeterministicResponse:
        meses = self.executive_summary_repository.obtener_mes_resumen()
        best = next(row for row in meses if row["ranking_actividad"] == 1)
        answer = (
            f"{best['nombre_mes']} fue el mes con mayor actividad del ejercicio {best['anio']} "
            f"con {best['movimientos']:,} movimientos registrados."
        )
        return DeterministicResponse(
            answer=answer,
            data=best,
            sources=["MES_RESUMEN", "EXECUTIVE_SUMMARY"],
        )

    def _worst_month(self, _match: IntentMatch, _entities: ExtractedEntities) -> DeterministicResponse:
        meses = self.executive_summary_repository.obtener_mes_resumen()
        worst = max(meses, key=lambda row: row["ranking_actividad"])
        answer = (
            f"El mes con menor actividad registrada fue {worst['nombre_mes'].lower()} "
            f"con {worst['movimientos']:,} movimientos."
        )
        return DeterministicResponse(
            answer=answer,
            data=worst,
            sources=["MES_RESUMEN", "EXECUTIVE_SUMMARY"],
        )

    def _month_analysis(
        self,
        _match: IntentMatch,
        entities: ExtractedEntities,
    ) -> DeterministicResponse:
        metadata = self.metadata_service.get_dataset_summary()
        anio = entities.year or metadata["anios"][-1]
        mes = entities.month
        if mes is None:
            mes = int(metadata["fecha_maxima"].split("-")[1])

        meses = self.executive_summary_repository.obtener_mes_resumen()
        mes_data = next(
            (row for row in meses if row["anio"] == anio and row["mes"] == mes),
            None,
        )
        if mes_data is None:
            nombre_mes = self.MESES.get(mes, str(mes))
            answer = (
                f"No se encontraron movimientos consolidados para {nombre_mes} de {anio} "
                f"en la capa ejecutiva."
            )
            return DeterministicResponse(
                answer=answer,
                data=None,
                sources=["MES_RESUMEN", "METADATA"],
            )

        nombre_mes = mes_data["nombre_mes"].lower()
        volumen_millones = self._format_millions(mes_data["monto_total"])
        ranking = mes_data["ranking_actividad"]
        actividad_texto = (
            "uno de los meses con mayor actividad del ejercicio"
            if ranking <= 3
            else "un mes dentro del rango habitual de actividad del ejercicio"
        )
        answer = (
            f"Durante {nombre_mes} de {anio} se registraron {mes_data['movimientos']:,} "
            f"movimientos por un volumen de {volumen_millones}. "
            f"Este periodo represento {actividad_texto}."
        )
        return DeterministicResponse(
            answer=answer,
            data=mes_data,
            sources=["MES_RESUMEN", "METADATA", "EXECUTIVE_SUMMARY"],
        )

    def _data_coverage(self, _match: IntentMatch, _entities: ExtractedEntities) -> DeterministicResponse:
        coverage = self._serialize(self.metadata_service.get_dataset_summary())
        answer = (
            f"La cobertura de datos abarca del {coverage['fecha_minima']} al "
            f"{coverage['fecha_maxima']} con {coverage['registros']:,} movimientos, "
            f"{coverage['clientes']:,} clientes, {coverage['proveedores']:,} proveedores "
            f"y {coverage['cuentas']:,} cuentas contables."
        )
        return DeterministicResponse(
            answer=answer,
            data={"coverage": coverage},
            sources=["METADATA"],
        )

    def _kpis(self, _match: IntentMatch, _entities: ExtractedEntities) -> DeterministicResponse:
        kpis = self._serialize(self.analytics_service.get_kpis())
        answer = (
            f"El dataset contiene {kpis['movimientos']:,} movimientos, "
            f"{kpis['clientes']:,} clientes, {kpis['proveedores']:,} proveedores, "
            f"{kpis['cuentas']:,} cuentas y {kpis['divisas']:,} divisas operativas."
        )
        return DeterministicResponse(
            answer=answer,
            data=kpis,
            sources=["KPIS", "FACT_TABLES"],
        )

    def _kpis_ejecutivos(self, _match: IntentMatch, _entities: ExtractedEntities) -> DeterministicResponse:
        kpis = self._serialize(self.analytics_service.get_kpis_ejecutivos())
        cliente = kpis["cliente_principal"]
        answer = (
            f"El volumen total consolidado es {Decimal(kpis['volumen_total']):,.2f}. "
            f"El cliente principal es {cliente['nombre']} con {cliente['movimientos']:,} movimientos. "
            f"El mes de mayor actividad fue {kpis['mes_mayor_actividad']['mes']:02d}/"
            f"{kpis['mes_mayor_actividad']['anio']} con "
            f"{kpis['mes_mayor_actividad']['movimientos']:,} movimientos."
        )
        return DeterministicResponse(
            answer=answer,
            data=kpis,
            sources=["KPIS_EJECUTIVOS", "EXECUTIVE_SUMMARY"],
        )

    def _insights(self, _match: IntentMatch, _entities: ExtractedEntities) -> DeterministicResponse:
        insights = self._serialize(self.insights_engine.generate_insights())
        lines = [str(item["mensaje"]) for item in insights[:5]]
        answer = "Principales insights detectados:\n- " + "\n- ".join(lines)
        return DeterministicResponse(
            answer=answer,
            data=insights,
            sources=["INSIGHTS", "KPIS_EJECUTIVOS"],
        )

    def _cliente_crecimiento(self, _match: IntentMatch, _entities: ExtractedEntities) -> DeterministicResponse:
        context = self.insights_repository.fetch_trends_context()
        nombre = str(context["crec_cliente_nombre"])
        variacion = Decimal(str(context["crec_cliente_pct"]))
        answer = (
            f"El cliente con mayor crecimiento relativo fue {nombre} "
            f"con una variacion de {variacion:,.2f}%."
        )
        return DeterministicResponse(
            answer=answer,
            data={
                "cliente_codigo": context["crec_cliente_codigo"],
                "cliente_nombre": nombre,
                "variacion_pct": float(variacion),
            },
            sources=["INSIGHTS", "FACT_CLIENTE_MES"],
        )

    def _cliente_caida(self, _match: IntentMatch, _entities: ExtractedEntities) -> DeterministicResponse:
        row = self._fetch_extremo_variacion("cliente")
        answer = (
            f"El cliente con mayor caida relativa fue {row['nombre']} "
            f"con una variacion de {row['variacion_pct']:,.2f}%."
        )
        return DeterministicResponse(
            answer=answer,
            data=row,
            sources=["FACT_CLIENTE_MES", "EXECUTIVE_SUMMARY"],
        )

    def _proveedor_crecimiento(self, _match: IntentMatch, _entities: ExtractedEntities) -> DeterministicResponse:
        context = self.insights_repository.fetch_trends_context()
        nombre = str(context["crec_proveedor_nombre"])
        variacion = Decimal(str(context["crec_proveedor_pct"]))
        answer = (
            f"El proveedor con mayor crecimiento relativo fue {nombre} "
            f"con una variacion de {variacion:,.2f}%."
        )
        return DeterministicResponse(
            answer=answer,
            data={
                "proveedor_codigo": context["crec_proveedor_codigo"],
                "proveedor_nombre": nombre,
                "variacion_pct": float(variacion),
            },
            sources=["INSIGHTS", "FACT_PROVEEDOR_MES"],
        )

    def _proveedor_caida(self, _match: IntentMatch, _entities: ExtractedEntities) -> DeterministicResponse:
        row = self._fetch_extremo_variacion("proveedor")
        answer = (
            f"El proveedor con mayor caida relativa fue {row['nombre']} "
            f"con una variacion de {row['variacion_pct']:,.2f}%."
        )
        return DeterministicResponse(
            answer=answer,
            data=row,
            sources=["FACT_PROVEEDOR_MES", "EXECUTIVE_SUMMARY"],
        )

    def _resumen_mensual(self, _match: IntentMatch, _entities: ExtractedEntities) -> DeterministicResponse:
        rows = self._serialize(self.analytics_service.get_resumen_mensual())
        if not rows:
            answer = "No hay resumen mensual disponible en la capa analitica."
            return DeterministicResponse(answer=answer, data=[], sources=["RESUMEN_MENSUAL"])

        destacados = rows[:3]
        fragmentos = [
            f"{self.MESES.get(int(row['mes']), row['mes'])} {row['anio']}: {row['movimientos']:,} movimientos"
            for row in destacados
        ]
        answer = "Resumen mensual consolidado: " + "; ".join(fragmentos) + "."
        return DeterministicResponse(
            answer=answer,
            data=rows,
            sources=["MES_RESUMEN", "RESUMEN_MENSUAL"],
        )

    def _unsupported(self, match: IntentMatch, _entities: ExtractedEntities) -> DeterministicResponse:
        return DeterministicResponse(
            answer=(
                f"La intencion {match.intent.value} no tiene plantilla deterministica configurada."
            ),
            data=None,
            sources=[],
        )

    def _fetch_extremo_variacion(self, dimension: str) -> dict[str, Any]:
        table_map = {
            "cliente": ("fact_cliente_mes", "cliente_codigo", "cliente_nombre"),
            "proveedor": ("fact_proveedor_mes", "proveedor_codigo", "proveedor_nombre"),
        }
        table, code_col, name_col = table_map[dimension]
        row = self.insights_repository.session.execute(
            text(
                f"""
                WITH rangos AS (
                    SELECT
                        {code_col} AS codigo,
                        {name_col} AS nombre,
                        MIN(movimientos) AS min_mov,
                        MAX(movimientos) AS max_mov
                    FROM {table}
                    GROUP BY {code_col}, {name_col}
                    HAVING COUNT(*) >= 2 AND MAX(movimientos) > MIN(movimientos) AND MIN(movimientos) > 0
                )
                SELECT
                    codigo,
                    nombre,
                    ROUND(((min_mov - max_mov)::numeric / max_mov) * 100, 2) AS variacion_pct
                FROM rangos
                ORDER BY variacion_pct ASC
                LIMIT 1
                """
            )
        ).mappings().one()
        return {
            "codigo": row["codigo"],
            "nombre": row["nombre"],
            "variacion_pct": float(row["variacion_pct"]),
        }

    def _default_year(self) -> int:
        metadata = self.metadata_service.get_dataset_summary()
        return metadata["anios"][-1]

    @staticmethod
    def _format_millions(amount: Any) -> str:
        value = float(amount) / 1_000_000
        return f"{value:,.0f} millones"

    @staticmethod
    def _serialize(value: Any) -> Any:
        if isinstance(value, BaseModel):
            return value.model_dump(mode="json")
        if isinstance(value, list):
            return [DeterministicResponseEngine._serialize(item) for item in value]
        if isinstance(value, dict):
            return {
                key: DeterministicResponseEngine._serialize(item)
                for key, item in value.items()
            }
        return value
