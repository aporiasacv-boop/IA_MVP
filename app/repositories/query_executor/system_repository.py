import calendar
from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.observability.db_timing import track_database_call

SYSTEM_CAPABILITY_KEYS: tuple[str, ...] = (
    "clientes",
    "proveedores",
    "cuentas",
    "kpis",
    "top_clientes",
    "top_proveedores",
    "actividad_mensual",
    "insights",
)


class SystemRepository:
    """Consultas determinísticas sobre capacidades, cobertura y volumen del dataset.

    Fuentes del Data Mart:
    - mv_resumen_mensual: movimientos agregados y rango temporal (sin movimientos_diario).
    - fact_cliente / fact_proveedor: conteos dimensionales.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_dataset_info(self) -> dict:
        def _query() -> dict:
            row = self.session.execute(
                text(
                    """
                    WITH resumen AS (
                        SELECT COALESCE(SUM(movimientos), 0) AS total_movimientos
                        FROM mv_resumen_mensual
                    )
                    SELECT
                        resumen.total_movimientos,
                        (SELECT COUNT(*) FROM fact_cliente) AS total_clientes,
                        (SELECT COUNT(*) FROM fact_proveedor) AS total_proveedores
                    FROM resumen
                    """
                )
            ).mappings().one()
            return {
                "total_movimientos": int(row["total_movimientos"]),
                "total_clientes": int(row["total_clientes"]),
                "total_proveedores": int(row["total_proveedores"]),
            }

        return track_database_call(_query)

    def get_data_coverage(self) -> dict:
        def _query() -> dict:
            row = self.session.execute(
                text(
                    """
                    SELECT
                        MIN(anio * 100 + mes) AS periodo_min,
                        MAX(anio * 100 + mes) AS periodo_max
                    FROM mv_resumen_mensual
                    """
                )
            ).mappings().one()
            min_anio, min_mes = self._decode_period(row["periodo_min"])
            max_anio, max_mes = self._decode_period(row["periodo_max"])
            return {
                "fecha_min": self._first_day(min_anio, min_mes).isoformat(),
                "fecha_max": self._last_day(max_anio, max_mes).isoformat(),
            }

        return track_database_call(_query)

    def get_system_capabilities(self) -> dict:
        return {
            key: True
            for key in SYSTEM_CAPABILITY_KEYS
        }

    @staticmethod
    def _decode_period(period_key: int | None) -> tuple[int, int]:
        if not period_key:
            return 1, 1
        return int(period_key // 100), int(period_key % 100)

    @staticmethod
    def _first_day(anio: int, mes: int) -> date:
        return date(anio, mes, 1)

    @staticmethod
    def _last_day(anio: int, mes: int) -> date:
        last_day = calendar.monthrange(anio, mes)[1]
        return date(anio, mes, last_day)
