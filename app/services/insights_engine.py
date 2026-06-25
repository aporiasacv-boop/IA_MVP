from datetime import datetime
from decimal import Decimal

from app.repositories.insights_repository import InsightsRepository
from app.schemas.insights import InsightResponse, InsightsResumenResponse

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


class InsightsEngine:
    def __init__(self, repository: InsightsRepository) -> None:
        self.repository = repository

    def generate_insights(self) -> list[InsightResponse]:
        context = self.repository.fetch_full_context()
        generated_at = datetime.now()
        insights = [
            self._insight_concentracion_clientes(context, generated_at),
            self._insight_concentracion_clientes_top10(context, generated_at),
            self._insight_mes_pico_actividad(context, generated_at),
            self._insight_mes_pico_volumen(context, generated_at),
            self._insight_cliente_dominante(context, generated_at),
            self._insight_proveedor_dominante(context, generated_at),
            self._insight_cuenta_dominante(context, generated_at),
            self._insight_cliente_mayor_crecimiento(context, generated_at),
            self._insight_proveedor_mayor_crecimiento(context, generated_at),
            self._insight_cuenta_mayor_crecimiento(context, generated_at),
            self._insight_mes_atipico(context, generated_at),
        ]
        return insights

    def generate_resumen(self) -> InsightsResumenResponse:
        insights = self.generate_insights()
        return self.summarize(insights)

    def summarize(self, insights: list[InsightResponse]) -> InsightsResumenResponse:
        counts = {"critica": 0, "alta": 0, "media": 0, "baja": 0}
        for insight in insights:
            key = insight.severidad.lower()
            if key in counts:
                counts[key] += 1
        return InsightsResumenResponse(
            total_insights=len(insights),
            criticos=counts["critica"],
            altos=counts["alta"],
            medios=counts["media"],
            bajos=counts["baja"],
        )

    def _insight_concentracion_clientes(
        self, context: dict, generated_at: datetime
    ) -> InsightResponse:
        participacion = Decimal(str(context["top_5_clientes_participacion"]))
        return InsightResponse(
            tipo="concentracion_clientes",
            categoria="clientes",
            severidad=self._severidad_concentracion(participacion),
            titulo="Concentracion en clientes principales",
            mensaje=(
                f"Los 5 principales clientes representan el {participacion}% "
                f"del volumen registrado de clientes."
            ),
            valor=participacion,
            fecha_generacion=generated_at,
        )

    def _insight_concentracion_clientes_top10(
        self, context: dict, generated_at: datetime
    ) -> InsightResponse:
        participacion = Decimal(str(context["top_10_clientes_participacion"]))
        return InsightResponse(
            tipo="concentracion_clientes_top10",
            categoria="clientes",
            severidad=self._severidad_concentracion(participacion),
            titulo="Concentracion ampliada de clientes",
            mensaje=(
                f"Los 10 principales clientes concentran el {participacion}% "
                f"del volumen registrado de clientes."
            ),
            valor=participacion,
            fecha_generacion=generated_at,
        )

    def _insight_mes_pico_actividad(
        self, context: dict, generated_at: datetime
    ) -> InsightResponse:
        mes = int(context["actividad_mes"])
        anio = int(context["actividad_anio"])
        movimientos = int(context["actividad_movimientos"])
        nombre_mes = MESES.get(mes, str(mes))
        return InsightResponse(
            tipo="mes_pico_actividad",
            categoria="temporal",
            severidad="baja",
            titulo="Mes pico de actividad",
            mensaje=(
                f"{nombre_mes} fue el mes con mayor actividad con "
                f"{movimientos:,} movimientos en {anio}."
            ),
            valor=movimientos,
            fecha_generacion=generated_at,
        )

    def _insight_mes_pico_volumen(
        self, context: dict, generated_at: datetime
    ) -> InsightResponse:
        mes = int(context["volumen_mes"])
        anio = int(context["volumen_anio"])
        monto = Decimal(str(context["volumen_mes_total"]))
        nombre_mes = MESES.get(mes, str(mes))
        return InsightResponse(
            tipo="mes_pico_volumen",
            categoria="temporal",
            severidad="baja",
            titulo="Mes pico de volumen",
            mensaje=(
                f"{nombre_mes} registr\u00f3 el mayor volumen economico del ejercicio "
                f"{anio} con {monto:,.2f}."
            ),
            valor=monto,
            fecha_generacion=generated_at,
        )

    def _insight_cliente_dominante(
        self, context: dict, generated_at: datetime
    ) -> InsightResponse:
        movimientos = int(context["cliente_movimientos"])
        nombre = str(context["cliente_nombre"])
        codigo = str(context["cliente_codigo"])
        return InsightResponse(
            tipo="cliente_dominante",
            categoria="clientes",
            severidad="media",
            titulo="Cliente dominante",
            mensaje=(
                f"{nombre} ({codigo}) lidera la actividad con "
                f"{movimientos:,} movimientos."
            ),
            valor=movimientos,
            fecha_generacion=generated_at,
        )

    def _insight_proveedor_dominante(
        self, context: dict, generated_at: datetime
    ) -> InsightResponse:
        movimientos = int(context["proveedor_movimientos"])
        nombre = str(context["proveedor_nombre"])
        codigo = str(context["proveedor_codigo"])
        return InsightResponse(
            tipo="proveedor_dominante",
            categoria="proveedores",
            severidad="media",
            titulo="Proveedor dominante",
            mensaje=(
                f"{nombre} ({codigo}) concentra la mayor actividad de proveedores "
                f"con {movimientos:,} movimientos."
            ),
            valor=movimientos,
            fecha_generacion=generated_at,
        )

    def _insight_cuenta_dominante(
        self, context: dict, generated_at: datetime
    ) -> InsightResponse:
        movimientos = int(context["cuenta_movimientos"])
        nombre = str(context["cuenta_nombre"])
        codigo = str(context["cuenta_codigo"])
        return InsightResponse(
            tipo="cuenta_dominante",
            categoria="cuentas",
            severidad="media",
            titulo="Cuenta dominante",
            mensaje=(
                f"{nombre} ({codigo}) es la cuenta con mayor actividad "
                f"con {movimientos:,} movimientos."
            ),
            valor=movimientos,
            fecha_generacion=generated_at,
        )

    def _insight_cliente_mayor_crecimiento(
        self, context: dict, generated_at: datetime
    ) -> InsightResponse:
        crecimiento = Decimal(str(context["crec_cliente_pct"]))
        nombre = str(context["crec_cliente_nombre"])
        codigo = str(context["crec_cliente_codigo"])
        return InsightResponse(
            tipo="cliente_mayor_crecimiento",
            categoria="tendencias",
            severidad=self._severidad_crecimiento(crecimiento),
            titulo="Cliente con mayor crecimiento",
            mensaje=(
                f"{nombre} ({codigo}) registro el mayor crecimiento relativo del anio "
                f"con una variacion de {crecimiento}% entre su mes de menor y mayor actividad."
            ),
            valor=crecimiento,
            fecha_generacion=generated_at,
        )

    def _insight_proveedor_mayor_crecimiento(
        self, context: dict, generated_at: datetime
    ) -> InsightResponse:
        crecimiento = Decimal(str(context["crec_proveedor_pct"]))
        nombre = str(context["crec_proveedor_nombre"])
        codigo = str(context["crec_proveedor_codigo"])
        return InsightResponse(
            tipo="proveedor_mayor_crecimiento",
            categoria="tendencias",
            severidad=self._severidad_crecimiento(crecimiento),
            titulo="Proveedor con mayor crecimiento",
            mensaje=(
                f"{nombre} ({codigo}) registro el mayor crecimiento relativo del anio "
                f"con una variacion de {crecimiento}% entre su mes de menor y mayor actividad."
            ),
            valor=crecimiento,
            fecha_generacion=generated_at,
        )

    def _insight_cuenta_mayor_crecimiento(
        self, context: dict, generated_at: datetime
    ) -> InsightResponse:
        crecimiento = Decimal(str(context["crec_cuenta_pct"]))
        nombre = str(context["crec_cuenta_nombre"])
        codigo = str(context["crec_cuenta_codigo"])
        return InsightResponse(
            tipo="cuenta_mayor_crecimiento",
            categoria="tendencias",
            severidad=self._severidad_crecimiento(crecimiento),
            titulo="Cuenta con mayor crecimiento",
            mensaje=(
                f"{nombre} ({codigo}) registro el mayor crecimiento relativo del anio "
                f"con una variacion de {crecimiento}% entre su mes de menor y mayor actividad."
            ),
            valor=crecimiento,
            fecha_generacion=generated_at,
        )

    def _insight_mes_atipico(
        self, context: dict, generated_at: datetime
    ) -> InsightResponse:
        mes = int(context["atipico_mes"])
        anio = int(context["atipico_anio"])
        desviacion = Decimal(str(context["atipico_desviacion_pct"]))
        desviacion_abs = Decimal(str(context["atipico_desviacion_abs_pct"]))
        nombre_mes = MESES.get(mes, str(mes))
        if desviacion >= 0:
            comparacion = f"{desviacion_abs}% superior al promedio anual"
        else:
            comparacion = f"{desviacion_abs}% inferior al promedio anual"
        return InsightResponse(
            tipo="mes_atipico",
            categoria="anomalias",
            severidad=self._severidad_desviacion(desviacion_abs),
            titulo="Mes atipico de actividad",
            mensaje=(
                f"{nombre_mes} de {anio} presento una actividad {comparacion}."
            ),
            valor=desviacion_abs,
            fecha_generacion=generated_at,
        )

    @staticmethod
    def _severidad_concentracion(participacion: Decimal) -> str:
        if participacion >= Decimal("85"):
            return "critica"
        if participacion >= Decimal("70"):
            return "alta"
        if participacion >= Decimal("50"):
            return "media"
        return "baja"

    @staticmethod
    def _severidad_crecimiento(crecimiento: Decimal) -> str:
        if crecimiento >= Decimal("200"):
            return "critica"
        if crecimiento >= Decimal("100"):
            return "alta"
        if crecimiento >= Decimal("50"):
            return "media"
        return "baja"

    @staticmethod
    def _severidad_desviacion(desviacion_abs: Decimal) -> str:
        if desviacion_abs >= Decimal("25"):
            return "critica"
        if desviacion_abs >= Decimal("20"):
            return "alta"
        if desviacion_abs >= Decimal("10"):
            return "media"
        return "baja"
