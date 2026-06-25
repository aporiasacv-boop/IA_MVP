from sqlalchemy import text
from sqlalchemy.orm import Session


class InsightsRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def fetch_insights_context(self) -> dict:
        row = self.session.execute(
            text(
                """
                WITH mes_actividad AS (
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
                        ELSE ROUND((top5.total / volumen_clientes.total) * 100, 2)
                    END AS top_5_clientes_participacion,
                    CASE
                        WHEN volumen_clientes.total = 0 THEN 0
                        ELSE ROUND((top10.total / volumen_clientes.total) * 100, 2)
                    END AS top_10_clientes_participacion
                FROM mes_actividad
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

    def fetch_trends_context(self) -> dict:
        row = self.session.execute(
            text(
                """
                WITH cliente_rangos AS (
                    SELECT
                        cliente_codigo,
                        cliente_nombre,
                        MIN(movimientos) AS min_mov,
                        MAX(movimientos) AS max_mov
                    FROM fact_cliente_mes
                    GROUP BY cliente_codigo, cliente_nombre
                    HAVING COUNT(*) >= 2 AND MIN(movimientos) > 0 AND MAX(movimientos) > MIN(movimientos)
                ),
                cliente_crec AS (
                    SELECT
                        cliente_codigo,
                        cliente_nombre,
                        ROUND(((max_mov - min_mov)::numeric / min_mov) * 100, 2) AS crecimiento_pct
                    FROM cliente_rangos
                    ORDER BY crecimiento_pct DESC
                    LIMIT 1
                ),
                proveedor_rangos AS (
                    SELECT
                        proveedor_codigo,
                        proveedor_nombre,
                        MIN(movimientos) AS min_mov,
                        MAX(movimientos) AS max_mov
                    FROM fact_proveedor_mes
                    GROUP BY proveedor_codigo, proveedor_nombre
                    HAVING COUNT(*) >= 2 AND MIN(movimientos) > 0 AND MAX(movimientos) > MIN(movimientos)
                ),
                proveedor_crec AS (
                    SELECT
                        proveedor_codigo,
                        proveedor_nombre,
                        ROUND(((max_mov - min_mov)::numeric / min_mov) * 100, 2) AS crecimiento_pct
                    FROM proveedor_rangos
                    ORDER BY crecimiento_pct DESC
                    LIMIT 1
                ),
                cuenta_rangos AS (
                    SELECT
                        cuenta_codigo,
                        cuenta_nombre,
                        MIN(movimientos) AS min_mov,
                        MAX(movimientos) AS max_mov
                    FROM fact_cuenta_mes
                    GROUP BY cuenta_codigo, cuenta_nombre
                    HAVING COUNT(*) >= 2 AND MIN(movimientos) > 0 AND MAX(movimientos) > MIN(movimientos)
                ),
                cuenta_crec AS (
                    SELECT
                        cuenta_codigo,
                        cuenta_nombre,
                        ROUND(((max_mov - min_mov)::numeric / min_mov) * 100, 2) AS crecimiento_pct
                    FROM cuenta_rangos
                    ORDER BY crecimiento_pct DESC
                    LIMIT 1
                ),
                promedio_anual AS (
                    SELECT AVG(movimientos)::numeric AS avg_mov
                    FROM mv_resumen_mensual
                ),
                mes_atipico AS (
                    SELECT
                        r.anio,
                        r.mes,
                        r.movimientos,
                        ROUND(((r.movimientos - p.avg_mov) / p.avg_mov) * 100, 2) AS desviacion_pct,
                        ROUND(ABS((r.movimientos - p.avg_mov) / p.avg_mov) * 100, 2) AS desviacion_abs_pct
                    FROM mv_resumen_mensual r
                    CROSS JOIN promedio_anual p
                    ORDER BY ABS((r.movimientos - p.avg_mov) / p.avg_mov) DESC
                    LIMIT 1
                )
                SELECT
                    cliente_crec.cliente_codigo AS crec_cliente_codigo,
                    cliente_crec.cliente_nombre AS crec_cliente_nombre,
                    cliente_crec.crecimiento_pct AS crec_cliente_pct,
                    proveedor_crec.proveedor_codigo AS crec_proveedor_codigo,
                    proveedor_crec.proveedor_nombre AS crec_proveedor_nombre,
                    proveedor_crec.crecimiento_pct AS crec_proveedor_pct,
                    cuenta_crec.cuenta_codigo AS crec_cuenta_codigo,
                    cuenta_crec.cuenta_nombre AS crec_cuenta_nombre,
                    cuenta_crec.crecimiento_pct AS crec_cuenta_pct,
                    mes_atipico.anio AS atipico_anio,
                    mes_atipico.mes AS atipico_mes,
                    mes_atipico.movimientos AS atipico_movimientos,
                    mes_atipico.desviacion_pct AS atipico_desviacion_pct,
                    mes_atipico.desviacion_abs_pct AS atipico_desviacion_abs_pct
                FROM cliente_crec
                CROSS JOIN proveedor_crec
                CROSS JOIN cuenta_crec
                CROSS JOIN mes_atipico
                """
            )
        ).mappings().one()
        return dict(row)

    def fetch_full_context(self) -> dict:
        base = self.fetch_insights_context()
        trends = self.fetch_trends_context()
        return {**base, **trends}
