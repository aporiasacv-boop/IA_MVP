from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.repositories.executive_summary_repository import ExecutiveSummaryRepository

EXECUTIVE_SUMMARY_TABLES = [
    "cliente_resumen",
    "proveedor_resumen",
    "cuenta_resumen",
    "mes_resumen",
]

MES_NOMBRE_SQL = """
CASE mes
    WHEN 1 THEN 'Enero'
    WHEN 2 THEN 'Febrero'
    WHEN 3 THEN 'Marzo'
    WHEN 4 THEN 'Abril'
    WHEN 5 THEN 'Mayo'
    WHEN 6 THEN 'Junio'
    WHEN 7 THEN 'Julio'
    WHEN 8 THEN 'Agosto'
    WHEN 9 THEN 'Septiembre'
    WHEN 10 THEN 'Octubre'
    WHEN 11 THEN 'Noviembre'
    WHEN 12 THEN 'Diciembre'
    ELSE 'Desconocido'
END
"""


class ExecutiveSummaryService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = ExecutiveSummaryRepository(session)

    def truncate_summary_tables(self) -> None:
        tables = ", ".join(EXECUTIVE_SUMMARY_TABLES)
        self.session.execute(text(f"TRUNCATE TABLE {tables}"))

    def build_cliente_resumen(self, updated_at: datetime) -> None:
        self.session.execute(
            text(
                f"""
                INSERT INTO cliente_resumen (
                    cliente_codigo,
                    cliente_nombre,
                    movimientos,
                    monto_total,
                    monto_promedio,
                    participacion_pct,
                    ranking,
                    primer_movimiento,
                    ultimo_movimiento,
                    fecha_actualizacion
                )
                WITH totals AS (
                    SELECT COALESCE(SUM(monto_total), 0) AS volumen_total
                    FROM fact_cliente
                ),
                fechas AS (
                    SELECT
                        cuenta_cliente AS cliente_codigo,
                        MIN(fecha) AS primer_movimiento,
                        MAX(fecha) AS ultimo_movimiento
                    FROM movimientos_diario
                    WHERE cuenta_cliente IS NOT NULL
                    GROUP BY cuenta_cliente
                ),
                ranked AS (
                    SELECT
                        fc.cliente_codigo,
                        fc.cliente_nombre,
                        fc.movimientos,
                        fc.monto_total,
                        fc.monto_promedio,
                        CASE
                            WHEN t.volumen_total = 0 THEN 0
                            ELSE ROUND((fc.monto_total / t.volumen_total) * 100, 4)
                        END AS participacion_pct,
                        ROW_NUMBER() OVER (
                            ORDER BY fc.movimientos DESC, fc.monto_total DESC
                        ) AS ranking,
                        f.primer_movimiento,
                        f.ultimo_movimiento
                    FROM fact_cliente fc
                    CROSS JOIN totals t
                    LEFT JOIN fechas f ON f.cliente_codigo = fc.cliente_codigo
                )
                SELECT
                    cliente_codigo,
                    cliente_nombre,
                    movimientos,
                    monto_total,
                    monto_promedio,
                    participacion_pct,
                    ranking::INTEGER,
                    primer_movimiento,
                    ultimo_movimiento,
                    :updated_at
                FROM ranked
                """
            ),
            {"updated_at": updated_at},
        )

    def build_proveedor_resumen(self, updated_at: datetime) -> None:
        self.session.execute(
            text(
                """
                INSERT INTO proveedor_resumen (
                    proveedor_codigo,
                    proveedor_nombre,
                    movimientos,
                    monto_total,
                    monto_promedio,
                    participacion_pct,
                    ranking,
                    primer_movimiento,
                    ultimo_movimiento,
                    fecha_actualizacion
                )
                WITH totals AS (
                    SELECT COALESCE(SUM(monto_total), 0) AS volumen_total
                    FROM fact_proveedor
                ),
                fechas AS (
                    SELECT
                        cuenta_proveedor AS proveedor_codigo,
                        MIN(fecha) AS primer_movimiento,
                        MAX(fecha) AS ultimo_movimiento
                    FROM movimientos_diario
                    WHERE cuenta_proveedor IS NOT NULL
                    GROUP BY cuenta_proveedor
                ),
                ranked AS (
                    SELECT
                        fp.proveedor_codigo,
                        fp.proveedor_nombre,
                        fp.movimientos,
                        fp.monto_total,
                        fp.monto_promedio,
                        CASE
                            WHEN t.volumen_total = 0 THEN 0
                            ELSE ROUND((fp.monto_total / t.volumen_total) * 100, 4)
                        END AS participacion_pct,
                        ROW_NUMBER() OVER (
                            ORDER BY fp.movimientos DESC, fp.monto_total DESC
                        ) AS ranking,
                        f.primer_movimiento,
                        f.ultimo_movimiento
                    FROM fact_proveedor fp
                    CROSS JOIN totals t
                    LEFT JOIN fechas f ON f.proveedor_codigo = fp.proveedor_codigo
                )
                SELECT
                    proveedor_codigo,
                    proveedor_nombre,
                    movimientos,
                    monto_total,
                    monto_promedio,
                    participacion_pct,
                    ranking::INTEGER,
                    primer_movimiento,
                    ultimo_movimiento,
                    :updated_at
                FROM ranked
                """
            ),
            {"updated_at": updated_at},
        )

    def build_cuenta_resumen(self, updated_at: datetime) -> None:
        self.session.execute(
            text(
                """
                INSERT INTO cuenta_resumen (
                    cuenta_codigo,
                    cuenta_nombre,
                    movimientos,
                    monto_total,
                    monto_promedio,
                    participacion_pct,
                    ranking,
                    fecha_actualizacion
                )
                WITH totals AS (
                    SELECT COALESCE(SUM(monto_total), 0) AS volumen_total
                    FROM fact_cuenta
                ),
                ranked AS (
                    SELECT
                        fc.cuenta_codigo,
                        fc.cuenta_nombre,
                        fc.movimientos,
                        fc.monto_total,
                        fc.monto_promedio,
                        CASE
                            WHEN t.volumen_total = 0 THEN 0
                            ELSE ROUND((fc.monto_total / t.volumen_total) * 100, 4)
                        END AS participacion_pct,
                        ROW_NUMBER() OVER (
                            ORDER BY fc.movimientos DESC, fc.monto_total DESC
                        ) AS ranking
                    FROM fact_cuenta fc
                    CROSS JOIN totals t
                )
                SELECT
                    cuenta_codigo,
                    cuenta_nombre,
                    movimientos,
                    monto_total,
                    monto_promedio,
                    participacion_pct,
                    ranking::INTEGER,
                    :updated_at
                FROM ranked
                """
            ),
            {"updated_at": updated_at},
        )

    def build_mes_resumen(self, updated_at: datetime) -> None:
        self.session.execute(
            text(
                f"""
                INSERT INTO mes_resumen (
                    anio,
                    mes,
                    nombre_mes,
                    movimientos,
                    monto_total,
                    monto_promedio,
                    participacion_pct,
                    ranking_actividad,
                    ranking_volumen,
                    fecha_actualizacion
                )
                WITH totals AS (
                    SELECT COALESCE(SUM(monto_total), 0) AS volumen_total
                    FROM fact_mes
                ),
                ranked AS (
                    SELECT
                        fm.anio,
                        fm.mes,
                        {MES_NOMBRE_SQL} AS nombre_mes,
                        fm.movimientos,
                        fm.monto_total,
                        fm.monto_promedio,
                        CASE
                            WHEN t.volumen_total = 0 THEN 0
                            ELSE ROUND((fm.monto_total / t.volumen_total) * 100, 4)
                        END AS participacion_pct,
                        ROW_NUMBER() OVER (
                            ORDER BY fm.movimientos DESC, fm.monto_total DESC
                        ) AS ranking_actividad,
                        ROW_NUMBER() OVER (
                            ORDER BY fm.monto_total DESC, fm.movimientos DESC
                        ) AS ranking_volumen
                    FROM fact_mes fm
                    CROSS JOIN totals t
                )
                SELECT
                    anio,
                    mes,
                    nombre_mes,
                    movimientos,
                    monto_total,
                    monto_promedio,
                    participacion_pct,
                    ranking_actividad::INTEGER,
                    ranking_volumen::INTEGER,
                    :updated_at
                FROM ranked
                ORDER BY anio, mes
                """
            ),
            {"updated_at": updated_at},
        )

    def rebuild_all(self, updated_at: datetime | None = None) -> dict[str, int]:
        timestamp = updated_at or datetime.now()
        self.truncate_summary_tables()
        self.build_cliente_resumen(timestamp)
        self.build_proveedor_resumen(timestamp)
        self.build_cuenta_resumen(timestamp)
        self.build_mes_resumen(timestamp)
        return {
            "cliente_resumen": self.repository.count_cliente_resumen(),
            "proveedor_resumen": self.repository.count_proveedor_resumen(),
            "cuenta_resumen": self.repository.count_cuenta_resumen(),
            "mes_resumen": self.repository.count_mes_resumen(),
        }
