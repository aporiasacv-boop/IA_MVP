from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from sqlalchemy import func, select, text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database.database import SessionLocal
from app.models.fact_tables import (
    FactCliente,
    FactClienteMes,
    FactCuenta,
    FactCuentaMes,
    FactDivisa,
    FactMes,
    FactProveedor,
    FactProveedorMes,
)

MATERIALIZED_VIEWS = [
    "mv_resumen_mensual",
    "mv_top_cuentas",
    "mv_top_clientes",
    "mv_top_proveedores",
    "mv_cliente_evolucion",
    "mv_proveedor_evolucion",
    "mv_cuenta_evolucion",
]

FACT_TABLES = [
    "fact_mes",
    "fact_cuenta",
    "fact_cliente",
    "fact_proveedor",
    "fact_divisa",
    "fact_cliente_mes",
    "fact_proveedor_mes",
    "fact_cuenta_mes",
]


def truncate_fact_tables(session) -> None:
    tables = ", ".join(FACT_TABLES)
    session.execute(text(f"TRUNCATE TABLE {tables}"))


def build_fact_mes(session, updated_at: datetime) -> None:
    session.execute(
        text(
            """
            INSERT INTO fact_mes (anio, mes, movimientos, monto_total, monto_promedio, fecha_actualizacion)
            SELECT
                anio,
                mes,
                COUNT(*)::INTEGER,
                COALESCE(SUM(ABS(monto)), 0),
                COALESCE(AVG(ABS(monto)), 0),
                :updated_at
            FROM movimientos_diario
            GROUP BY anio, mes
            ORDER BY anio, mes
            """
        ),
        {"updated_at": updated_at},
    )


def build_fact_cuenta(session, updated_at: datetime) -> None:
    session.execute(
        text(
            """
            INSERT INTO fact_cuenta (
                cuenta_codigo, cuenta_nombre, movimientos, monto_total, monto_promedio, fecha_actualizacion
            )
            SELECT
                account_display_value,
                MAX(nombre_cuenta),
                COUNT(*)::INTEGER,
                COALESCE(SUM(ABS(monto)), 0),
                COALESCE(AVG(ABS(monto)), 0),
                :updated_at
            FROM movimientos_diario
            GROUP BY account_display_value
            """
        ),
        {"updated_at": updated_at},
    )


def build_fact_cliente(session, updated_at: datetime) -> None:
    session.execute(
        text(
            """
            INSERT INTO fact_cliente (
                cliente_codigo, cliente_nombre, movimientos, monto_total, monto_promedio, fecha_actualizacion
            )
            SELECT
                cuenta_cliente,
                MAX(nombre_cliente),
                COUNT(*)::INTEGER,
                COALESCE(SUM(ABS(monto)), 0),
                COALESCE(AVG(ABS(monto)), 0),
                :updated_at
            FROM movimientos_diario
            WHERE cuenta_cliente IS NOT NULL
              AND nombre_cliente IS NOT NULL
            GROUP BY cuenta_cliente
            """
        ),
        {"updated_at": updated_at},
    )


def build_fact_proveedor(session, updated_at: datetime) -> None:
    session.execute(
        text(
            """
            INSERT INTO fact_proveedor (
                proveedor_codigo, proveedor_nombre, movimientos, monto_total, monto_promedio, fecha_actualizacion
            )
            SELECT
                cuenta_proveedor,
                MAX(nombre_proveedor),
                COUNT(*)::INTEGER,
                COALESCE(SUM(ABS(monto)), 0),
                COALESCE(AVG(ABS(monto)), 0),
                :updated_at
            FROM movimientos_diario
            WHERE cuenta_proveedor IS NOT NULL
              AND nombre_proveedor IS NOT NULL
            GROUP BY cuenta_proveedor
            """
        ),
        {"updated_at": updated_at},
    )


def build_fact_divisa(session, updated_at: datetime) -> None:
    session.execute(
        text(
            """
            INSERT INTO fact_divisa (divisa, movimientos, monto_total, monto_promedio, fecha_actualizacion)
            SELECT
                divisa,
                COUNT(*)::INTEGER,
                COALESCE(SUM(ABS(monto)), 0),
                COALESCE(AVG(ABS(monto)), 0),
                :updated_at
            FROM movimientos_diario
            GROUP BY divisa
            ORDER BY divisa
            """
        ),
        {"updated_at": updated_at},
    )


def build_fact_cliente_mes(session, updated_at: datetime) -> None:
    session.execute(
        text(
            """
            INSERT INTO fact_cliente_mes (
                anio, mes, cliente_codigo, cliente_nombre,
                movimientos, monto_total, monto_promedio, fecha_actualizacion
            )
            SELECT
                anio,
                mes,
                cuenta_cliente,
                MAX(nombre_cliente),
                COUNT(*)::INTEGER,
                COALESCE(SUM(ABS(monto)), 0),
                COALESCE(AVG(ABS(monto)), 0),
                :updated_at
            FROM movimientos_diario
            WHERE cuenta_cliente IS NOT NULL
              AND nombre_cliente IS NOT NULL
            GROUP BY anio, mes, cuenta_cliente
            """
        ),
        {"updated_at": updated_at},
    )


def build_fact_proveedor_mes(session, updated_at: datetime) -> None:
    session.execute(
        text(
            """
            INSERT INTO fact_proveedor_mes (
                anio, mes, proveedor_codigo, proveedor_nombre,
                movimientos, monto_total, monto_promedio, fecha_actualizacion
            )
            SELECT
                anio,
                mes,
                cuenta_proveedor,
                MAX(nombre_proveedor),
                COUNT(*)::INTEGER,
                COALESCE(SUM(ABS(monto)), 0),
                COALESCE(AVG(ABS(monto)), 0),
                :updated_at
            FROM movimientos_diario
            WHERE cuenta_proveedor IS NOT NULL
              AND nombre_proveedor IS NOT NULL
            GROUP BY anio, mes, cuenta_proveedor
            """
        ),
        {"updated_at": updated_at},
    )


def build_fact_cuenta_mes(session, updated_at: datetime) -> None:
    session.execute(
        text(
            """
            INSERT INTO fact_cuenta_mes (
                anio, mes, cuenta_codigo, cuenta_nombre,
                movimientos, monto_total, monto_promedio, fecha_actualizacion
            )
            SELECT
                anio,
                mes,
                account_display_value,
                MAX(nombre_cuenta),
                COUNT(*)::INTEGER,
                COALESCE(SUM(ABS(monto)), 0),
                COALESCE(AVG(ABS(monto)), 0),
                :updated_at
            FROM movimientos_diario
            GROUP BY anio, mes, account_display_value
            """
        ),
        {"updated_at": updated_at},
    )


def refresh_materialized_views(session) -> None:
    for view_name in MATERIALIZED_VIEWS:
        session.execute(text(f"REFRESH MATERIALIZED VIEW {view_name}"))


def count_rows(session, model) -> int:
    return session.scalar(select(func.count()).select_from(model)) or 0


def main() -> int:
    updated_at = datetime.now()
    print("Construyendo datamart IA_MVP v2...")
    print(f"Fecha de actualizacion: {updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print("")

    with SessionLocal() as session:
        print("Vaciando tablas fact...")
        truncate_fact_tables(session)
        session.commit()

        print("Recalculando agregaciones desde movimientos_diario...")
        build_fact_mes(session, updated_at)
        build_fact_cuenta(session, updated_at)
        build_fact_cliente(session, updated_at)
        build_fact_proveedor(session, updated_at)
        build_fact_divisa(session, updated_at)
        build_fact_cliente_mes(session, updated_at)
        build_fact_proveedor_mes(session, updated_at)
        build_fact_cuenta_mes(session, updated_at)
        session.commit()

        print("")
        print("Resultados fact tables v1:")
        print(f"  Fact Mes: {count_rows(session, FactMes)} filas")
        print(f"  Fact Cuenta: {count_rows(session, FactCuenta)} filas")
        print(f"  Fact Cliente: {count_rows(session, FactCliente)} filas")
        print(f"  Fact Proveedor: {count_rows(session, FactProveedor)} filas")
        print(f"  Fact Divisa: {count_rows(session, FactDivisa)} filas")

        print("")
        print("Resultados fact tables v2:")
        print(f"  Fact Cliente Mes: {count_rows(session, FactClienteMes)} filas")
        print(f"  Fact Proveedor Mes: {count_rows(session, FactProveedorMes)} filas")
        print(f"  Fact Cuenta Mes: {count_rows(session, FactCuentaMes)} filas")

        print("")
        print("Refrescando materialized views...")
        refresh_materialized_views(session)
        session.commit()
        print("Materialized Views refrescadas correctamente.")

    print("")
    print("[OK] Datamart v2 construido exitosamente")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
