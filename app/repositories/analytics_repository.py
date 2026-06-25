from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models.fact_tables import (
    FactCliente,
    FactCuenta,
    FactDivisa,
    FactProveedor,
)
from app.models.movimiento_diario import MovimientoDiario


class AnalyticsRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def count_movimientos(self) -> int:
        return self.session.scalar(select(func.count()).select_from(MovimientoDiario)) or 0

    def count_clientes(self) -> int:
        return self.session.scalar(select(func.count()).select_from(FactCliente)) or 0

    def count_proveedores(self) -> int:
        return self.session.scalar(select(func.count()).select_from(FactProveedor)) or 0

    def count_cuentas(self) -> int:
        return self.session.scalar(select(func.count()).select_from(FactCuenta)) or 0

    def count_divisas(self) -> int:
        return self.session.scalar(select(func.count()).select_from(FactDivisa)) or 0

    def fetch_top_clientes(self, limit: int) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT ranking, cliente_codigo, cliente_nombre, movimientos, monto_total, monto_promedio
                FROM mv_top_clientes
                ORDER BY ranking
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()
        return [dict(row) for row in rows]

    def fetch_top_proveedores(self, limit: int) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT ranking, proveedor_codigo, proveedor_nombre, movimientos, monto_total, monto_promedio
                FROM mv_top_proveedores
                ORDER BY ranking
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()
        return [dict(row) for row in rows]

    def fetch_top_cuentas(self, limit: int) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT ranking, cuenta_codigo, cuenta_nombre, movimientos, monto_total, monto_promedio
                FROM mv_top_cuentas
                ORDER BY ranking
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()
        return [dict(row) for row in rows]

    def fetch_evolucion_cliente(self, cliente_codigo: str) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT anio, mes, cliente_codigo, cliente_nombre, movimientos, monto_total, monto_promedio
                FROM mv_cliente_evolucion
                WHERE cliente_codigo = :cliente_codigo
                ORDER BY anio, mes
                """
            ),
            {"cliente_codigo": cliente_codigo},
        ).mappings().all()
        return [dict(row) for row in rows]

    def fetch_evolucion_proveedor(self, proveedor_codigo: str) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT anio, mes, proveedor_codigo, proveedor_nombre, movimientos, monto_total, monto_promedio
                FROM mv_proveedor_evolucion
                WHERE proveedor_codigo = :proveedor_codigo
                ORDER BY anio, mes
                """
            ),
            {"proveedor_codigo": proveedor_codigo},
        ).mappings().all()
        return [dict(row) for row in rows]

    def fetch_evolucion_cuenta(self, cuenta_codigo: str) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT anio, mes, cuenta_codigo, cuenta_nombre, movimientos, monto_total, monto_promedio
                FROM mv_cuenta_evolucion
                WHERE cuenta_codigo = :cuenta_codigo
                ORDER BY anio, mes
                """
            ),
            {"cuenta_codigo": cuenta_codigo},
        ).mappings().all()
        return [dict(row) for row in rows]

    def fetch_resumen_mensual(self) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT anio, mes, movimientos, monto_total, monto_promedio
                FROM mv_resumen_mensual
                ORDER BY anio, mes
                """
            )
        ).mappings().all()
        return [dict(row) for row in rows]

    def fetch_kpis_ejecutivos(self) -> dict:
        row = self.session.execute(
            text(
                """
                WITH resumen AS (
                    SELECT
                        COALESCE(SUM(monto_total), 0) AS volumen_total,
                        COALESCE(AVG(movimientos), 0) AS movimiento_promedio
                    FROM mv_resumen_mensual
                ),
                mes_actividad AS (
                    SELECT anio, mes, movimientos
                    FROM mv_resumen_mensual
                    ORDER BY movimientos DESC
                    LIMIT 1
                ),
                mes_volumen AS (
                    SELECT anio, mes, monto_total
                    FROM mv_resumen_mensual
                    ORDER BY monto_total DESC
                    LIMIT 1
                ),
                cliente AS (
                    SELECT cliente_codigo, cliente_nombre, movimientos, monto_total
                    FROM mv_top_clientes
                    WHERE ranking = 1
                ),
                proveedor AS (
                    SELECT proveedor_codigo, proveedor_nombre, movimientos, monto_total
                    FROM mv_top_proveedores
                    WHERE ranking = 1
                ),
                cuenta AS (
                    SELECT cuenta_codigo, cuenta_nombre, movimientos, monto_total
                    FROM mv_top_cuentas
                    WHERE ranking = 1
                ),
                volumen_clientes AS (
                    SELECT COALESCE(SUM(monto_total), 0) AS total
                    FROM fact_cliente
                ),
                top5 AS (
                    SELECT COALESCE(SUM(monto_total), 0) AS total
                    FROM mv_top_clientes
                    WHERE ranking <= 5
                ),
                top10 AS (
                    SELECT COALESCE(SUM(monto_total), 0) AS total
                    FROM mv_top_clientes
                    WHERE ranking <= 10
                )
                SELECT
                    resumen.volumen_total,
                    resumen.movimiento_promedio,
                    mes_actividad.anio AS actividad_anio,
                    mes_actividad.mes AS actividad_mes,
                    mes_actividad.movimientos AS actividad_movimientos,
                    mes_volumen.anio AS volumen_anio,
                    mes_volumen.mes AS volumen_mes,
                    mes_volumen.monto_total AS volumen_mes_total,
                    cliente.cliente_codigo,
                    cliente.cliente_nombre,
                    cliente.movimientos AS cliente_movimientos,
                    cliente.monto_total AS cliente_monto_total,
                    proveedor.proveedor_codigo,
                    proveedor.proveedor_nombre,
                    proveedor.movimientos AS proveedor_movimientos,
                    proveedor.monto_total AS proveedor_monto_total,
                    cuenta.cuenta_codigo,
                    cuenta.cuenta_nombre,
                    cuenta.movimientos AS cuenta_movimientos,
                    cuenta.monto_total AS cuenta_monto_total,
                    CASE
                        WHEN volumen_clientes.total = 0 THEN 0
                        ELSE ROUND((top5.total / volumen_clientes.total) * 100, 4)
                    END AS top_5_clientes_participacion,
                    CASE
                        WHEN volumen_clientes.total = 0 THEN 0
                        ELSE ROUND((top10.total / volumen_clientes.total) * 100, 4)
                    END AS top_10_clientes_participacion
                FROM resumen
                CROSS JOIN mes_actividad
                CROSS JOIN mes_volumen
                CROSS JOIN cliente
                CROSS JOIN proveedor
                CROSS JOIN cuenta
                CROSS JOIN volumen_clientes
                CROSS JOIN top5
                CROSS JOIN top10
                """
            )
        ).mappings().one()
        return dict(row)
