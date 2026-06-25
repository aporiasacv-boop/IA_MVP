from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models.fact_tables import FactCliente
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


class ClienteRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def count_clientes(self) -> int:
        return track_database_call(
            lambda: self.session.scalar(select(func.count()).select_from(FactCliente)) or 0,
        )

    def top_clientes(self, limit: int = 10) -> list[dict]:
        def _query() -> list[dict]:
            rows = self.session.execute(
                text(
                    """
                SELECT
                    ranking,
                    cliente_codigo,
                    cliente_nombre,
                    movimientos,
                    monto_total,
                    monto_promedio
                FROM mv_top_clientes
                ORDER BY ranking
                LIMIT :limit
                """
                ),
                {"limit": limit},
            ).mappings().all()
            return [_serialize_row(dict(row)) for row in rows]

        return track_database_call(_query)
