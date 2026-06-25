from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import func, select, text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database.database import SessionLocal
from app.models.movimiento_diario import MovimientoDiario


def print_section(title: str) -> None:
    print("")
    print("=" * 72)
    print(title)
    print("=" * 72)


def main() -> int:
    with SessionLocal() as session:
        total = session.scalar(select(func.count()).select_from(MovimientoDiario)) or 0

        print_section("VALIDACION DE CARGA - movimientos_diario")
        print(f"Total registros: {total:,}")

        if total == 0:
            print("No hay registros cargados.")
            return 1

        fecha_min, fecha_max = session.execute(
            select(func.min(MovimientoDiario.fecha), func.max(MovimientoDiario.fecha))
        ).one()
        print(f"Rango de fechas: {fecha_min} -> {fecha_max}")

        print_section("Conteo por mes")
        mes_rows = session.execute(
            select(MovimientoDiario.mes, func.count())
            .group_by(MovimientoDiario.mes)
            .order_by(MovimientoDiario.mes)
        ).all()
        for mes, count in mes_rows:
            print(f"  Mes {mes:02d}: {count:,}")

        print_section("Top 10 cuentas por movimientos")
        cuenta_rows = session.execute(
            select(
                MovimientoDiario.account_display_value,
                MovimientoDiario.nombre_cuenta,
                func.count().label("total"),
            )
            .group_by(MovimientoDiario.account_display_value, MovimientoDiario.nombre_cuenta)
            .order_by(func.count().desc())
            .limit(10)
        ).all()
        for codigo, nombre, count in cuenta_rows:
            print(f"  {codigo} | {nombre} | {count:,}")

        print_section("Top 10 proveedores por movimientos")
        proveedor_rows = session.execute(
            select(
                MovimientoDiario.cuenta_proveedor,
                MovimientoDiario.nombre_proveedor,
                func.count().label("total"),
            )
            .where(MovimientoDiario.nombre_proveedor.is_not(None))
            .group_by(MovimientoDiario.cuenta_proveedor, MovimientoDiario.nombre_proveedor)
            .order_by(func.count().desc())
            .limit(10)
        ).all()
        for cuenta, nombre, count in proveedor_rows:
            print(f"  {cuenta} | {nombre} | {count:,}")

        print_section("Top 10 clientes por movimientos")
        cliente_rows = session.execute(
            select(
                MovimientoDiario.cuenta_cliente,
                MovimientoDiario.nombre_cliente,
                func.count().label("total"),
            )
            .where(MovimientoDiario.nombre_cliente.is_not(None))
            .group_by(MovimientoDiario.cuenta_cliente, MovimientoDiario.nombre_cliente)
            .order_by(func.count().desc())
            .limit(10)
        ).all()
        for cuenta, nombre, count in cliente_rows:
            print(f"  {cuenta} | {nombre} | {count:,}")

        print("")
        print("Validacion completada.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
