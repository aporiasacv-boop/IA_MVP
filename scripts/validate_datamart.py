from __future__ import annotations

import sys
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


def print_section(title: str) -> None:
    print("")
    print("=" * 72)
    print(title)
    print("=" * 72)


def print_evolucion(session, view_name: str, codigo: str, label: str) -> None:
    print_section(f"Evolucion {label} ({codigo})")
    rows = session.execute(
        text(
            f"""
            SELECT anio, mes, movimientos, monto_total
            FROM {view_name}
            WHERE {"cliente_codigo" if "cliente" in view_name else "proveedor_codigo" if "proveedor" in view_name else "cuenta_codigo"} = :codigo
            ORDER BY anio, mes
            """
        ),
        {"codigo": codigo},
    ).all()
    if not rows:
        print(f"  Sin datos para {codigo}")
        return
    for anio, mes, movimientos, monto_total in rows:
        print(f"  {anio}-{mes:02d} | movimientos: {movimientos:,} | monto_total: {monto_total:,.2f}")


def print_top_por_mes(session, table_name: str, codigo_col: str, nombre_col: str, limit: int = 3) -> None:
    print_section(f"Top {limit} por mes - {table_name}")
    rows = session.execute(
        text(
            f"""
            SELECT anio, mes, {codigo_col}, {nombre_col}, movimientos, monto_total
            FROM (
                SELECT
                    anio,
                    mes,
                    {codigo_col},
                    {nombre_col},
                    movimientos,
                    monto_total,
                    ROW_NUMBER() OVER (
                        PARTITION BY anio, mes
                        ORDER BY movimientos DESC, monto_total DESC
                    ) AS ranking
                FROM {table_name}
            ) ranked
            WHERE ranking <= :limit
            ORDER BY anio, mes, ranking
            """
        ),
        {"limit": limit},
    ).all()
    current_period = None
    for anio, mes, codigo, nombre, movimientos, monto_total in rows:
        period = f"{anio}-{mes:02d}"
        if period != current_period:
            print(f"  Periodo {period}:")
            current_period = period
        print(f"    {codigo} | {nombre} | {movimientos:,} | {monto_total:,.2f}")


def main() -> int:
    with SessionLocal() as session:
        print_section("VALIDACION DATAMART V2 - IA_MVP")

        counts_v1 = {
            "fact_mes": session.scalar(select(func.count()).select_from(FactMes)) or 0,
            "fact_cuenta": session.scalar(select(func.count()).select_from(FactCuenta)) or 0,
            "fact_cliente": session.scalar(select(func.count()).select_from(FactCliente)) or 0,
            "fact_proveedor": session.scalar(select(func.count()).select_from(FactProveedor)) or 0,
            "fact_divisa": session.scalar(select(func.count()).select_from(FactDivisa)) or 0,
        }
        counts_v2 = {
            "fact_cliente_mes": session.scalar(select(func.count()).select_from(FactClienteMes)) or 0,
            "fact_proveedor_mes": session.scalar(select(func.count()).select_from(FactProveedorMes)) or 0,
            "fact_cuenta_mes": session.scalar(select(func.count()).select_from(FactCuentaMes)) or 0,
        }

        print_section("Filas por tabla fact v1")
        for table_name, total in counts_v1.items():
            print(f"  {table_name}: {total:,}")

        print_section("Filas por tabla fact v2")
        for table_name, total in counts_v2.items():
            print(f"  {table_name}: {total:,}")

        if any(total == 0 for total in {**counts_v1, **counts_v2}.values()):
            print("")
            print("[FAIL] Una o mas tablas fact estan vacias")
            return 1

        mv_counts = session.execute(
            text(
                """
                SELECT 'mv_resumen_mensual' AS nombre, COUNT(*) FROM mv_resumen_mensual
                UNION ALL
                SELECT 'mv_top_cuentas', COUNT(*) FROM mv_top_cuentas
                UNION ALL
                SELECT 'mv_top_clientes', COUNT(*) FROM mv_top_clientes
                UNION ALL
                SELECT 'mv_top_proveedores', COUNT(*) FROM mv_top_proveedores
                UNION ALL
                SELECT 'mv_cliente_evolucion', COUNT(*) FROM mv_cliente_evolucion
                UNION ALL
                SELECT 'mv_proveedor_evolucion', COUNT(*) FROM mv_proveedor_evolucion
                UNION ALL
                SELECT 'mv_cuenta_evolucion', COUNT(*) FROM mv_cuenta_evolucion
                """
            )
        ).all()

        print_section("Materialized views")
        for name, total in mv_counts:
            print(f"  {name}: {total:,}")

        print_evolucion(session, "mv_cliente_evolucion", "C0026", "COSTCO DE MEXICO")
        print_evolucion(session, "mv_cliente_evolucion", "C0027", "NUEVA WALMART DE MEXICO")
        print_evolucion(session, "mv_cuenta_evolucion", "20603001", "IVA TRASLADABLE POR COBRAR")

        print_top_por_mes(session, "fact_cliente_mes", "cliente_codigo", "cliente_nombre")
        print_top_por_mes(session, "fact_proveedor_mes", "proveedor_codigo", "proveedor_nombre")
        print_top_por_mes(session, "fact_cuenta_mes", "cuenta_codigo", "cuenta_nombre")

        print_section("Top 10 clientes global")
        cliente_rows = session.execute(
            text(
                """
                SELECT ranking, cliente_codigo, cliente_nombre, movimientos, monto_total
                FROM mv_top_clientes
                ORDER BY ranking
                LIMIT 10
                """
            )
        ).all()
        for ranking, codigo, nombre, movimientos, monto_total in cliente_rows:
            print(f"  #{ranking} {codigo} | {nombre} | {movimientos:,} | {monto_total:,.2f}")

        print("")
        print("[OK] Datamart v2 validado correctamente")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
