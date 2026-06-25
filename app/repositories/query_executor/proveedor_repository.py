from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models.fact_tables import FactProveedor
from app.observability.db_timing import track_database_call


def _serialize_row(row: dict) -> dict:
    serialized: dict = {}
    for key, value in row.items():
        if isinstance(value, Decimal):
            serialized[key] = float(value)
        elif isinstance(value, (datetime, date)):
            serialized[key] = value.isoformat()
        else:
            serialized[key] = value
    return serialized


class ProveedorRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def count_proveedores(self) -> int:
        return track_database_call(
            lambda: self.session.scalar(select(func.count()).select_from(FactProveedor)) or 0,
        )

    def top_proveedores(self, limit: int = 10) -> list[dict]:
        def _query() -> list[dict]:
            rows = self.session.execute(
                text(
                    """
                SELECT
                    ranking,
                    proveedor_codigo,
                    proveedor_nombre,
                    movimientos,
                    monto_total,
                    monto_promedio
                FROM mv_top_proveedores
                ORDER BY ranking
                LIMIT :limit
                """
                ),
                {"limit": limit},
            ).mappings().all()
            return [_serialize_row(dict(row)) for row in rows]

        return track_database_call(_query)

    def max_proveedor_mes(self, mes: int, anio: int | None = None) -> dict | None:
        def _query() -> dict | None:
            params: dict = {"mes": mes}
            anio_filter = ""
            if anio is not None:
                anio_filter = "AND anio = :anio"
                params["anio"] = anio

            row = self.session.execute(
                text(
                    f"""
                SELECT
                    anio,
                    mes,
                    proveedor_codigo,
                    proveedor_nombre,
                    movimientos,
                    monto_total,
                    monto_promedio
                FROM fact_proveedor_mes
                WHERE mes = :mes
                {anio_filter}
                ORDER BY movimientos DESC, ABS(monto_total) DESC
                LIMIT 1
                """
                ),
                params,
            ).mappings().first()

            if row is None:
                return None
            return _serialize_row(dict(row))

        return track_database_call(_query)
