from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models.executive_summary_tables import (
    ClienteResumen,
    CuentaResumen,
    MesResumen,
    ProveedorResumen,
)


class ExecutiveSummaryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def count_cliente_resumen(self) -> int:
        return self.session.scalar(select(func.count()).select_from(ClienteResumen)) or 0

    def count_proveedor_resumen(self) -> int:
        return self.session.scalar(select(func.count()).select_from(ProveedorResumen)) or 0

    def count_cuenta_resumen(self) -> int:
        return self.session.scalar(select(func.count()).select_from(CuentaResumen)) or 0

    def count_mes_resumen(self) -> int:
        return self.session.scalar(select(func.count()).select_from(MesResumen)) or 0

    def obtener_cliente_resumen(self) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT
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
                FROM cliente_resumen
                ORDER BY ranking
                """
            )
        ).mappings().all()
        return [dict(row) for row in rows]

    def obtener_proveedor_resumen(self) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT
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
                FROM proveedor_resumen
                ORDER BY ranking
                """
            )
        ).mappings().all()
        return [dict(row) for row in rows]

    def obtener_cuenta_resumen(self) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT
                    cuenta_codigo,
                    cuenta_nombre,
                    movimientos,
                    monto_total,
                    monto_promedio,
                    participacion_pct,
                    ranking,
                    fecha_actualizacion
                FROM cuenta_resumen
                ORDER BY ranking
                """
            )
        ).mappings().all()
        return [dict(row) for row in rows]

    def obtener_mes_resumen(self) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT
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
                FROM mes_resumen
                ORDER BY anio, mes
                """
            )
        ).mappings().all()
        return [dict(row) for row in rows]

    def obtener_top_clientes_resumen(self, limit: int = 10) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT
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
                FROM cliente_resumen
                ORDER BY ranking
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()
        return [dict(row) for row in rows]

    def obtener_bottom_clientes_resumen(self, limit: int = 10) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT
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
                FROM cliente_resumen
                ORDER BY ranking DESC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()
        return [dict(row) for row in rows]

    def obtener_top_proveedores_resumen(self, limit: int = 10) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT
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
                FROM proveedor_resumen
                ORDER BY ranking
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()
        return [dict(row) for row in rows]

    def obtener_bottom_proveedores_resumen(self, limit: int = 10) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT
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
                FROM proveedor_resumen
                ORDER BY ranking DESC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()
        return [dict(row) for row in rows]
