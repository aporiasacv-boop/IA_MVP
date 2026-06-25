from __future__ import annotations

import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database.database import SessionLocal
from app.services.executive_summary_service import ExecutiveSummaryService


def print_section(title: str) -> None:
    print("")
    print("=" * 72)
    print(title)
    print("=" * 72)


def main() -> int:
    started_at = time.perf_counter()
    updated_at = datetime.now()

    print("Construyendo capa de resumenes ejecutivos IA_MVP...")
    print(f"Fecha de actualizacion: {updated_at.strftime('%Y-%m-%d %H:%M:%S')}")

    with SessionLocal() as session:
        service = ExecutiveSummaryService(session)

        print_section("1. Vaciar tablas resumen")
        service.truncate_summary_tables()
        session.commit()
        print("  Tablas vaciadas: cliente_resumen, proveedor_resumen, cuenta_resumen, mes_resumen")

        print_section("2. Reconstruir tablas resumen")
        build_started = time.perf_counter()
        service.build_cliente_resumen(updated_at)
        service.build_proveedor_resumen(updated_at)
        service.build_cuenta_resumen(updated_at)
        service.build_mes_resumen(updated_at)
        session.commit()
        build_elapsed = time.perf_counter() - build_started
        print(f"  Reconstruccion completada en {build_elapsed:.2f}s")

        print_section("3. Validar registros")
        counts = {
            "cliente_resumen": service.repository.count_cliente_resumen(),
            "proveedor_resumen": service.repository.count_proveedor_resumen(),
            "cuenta_resumen": service.repository.count_cuenta_resumen(),
            "mes_resumen": service.repository.count_mes_resumen(),
        }
        for table_name, total in counts.items():
            status = "OK" if total > 0 else "VACIA"
            print(f"  {table_name}: {total:,} registros [{status}]")

        print_section("4. Metricas ejecutivas")
        top_cliente = service.repository.obtener_top_clientes_resumen(1)
        top_proveedor = service.repository.obtener_top_proveedores_resumen(1)
        top_cuenta = service.repository.obtener_cuenta_resumen()[:1]
        meses = service.repository.obtener_mes_resumen()
        mes_actividad = min(meses, key=lambda row: row["ranking_actividad"]) if meses else None

        if top_cliente:
            row = top_cliente[0]
            print(
                f"  Top cliente: #{row['ranking']} {row['cliente_nombre']} "
                f"({row['movimientos']:,} mov | {row['monto_total']:,.2f} | {row['participacion_pct']:.4f}%)"
            )
        if top_proveedor:
            row = top_proveedor[0]
            print(
                f"  Top proveedor: #{row['ranking']} {row['proveedor_nombre']} "
                f"({row['movimientos']:,} mov | {row['monto_total']:,.2f} | {row['participacion_pct']:.4f}%)"
            )
        if top_cuenta:
            row = top_cuenta[0]
            print(
                f"  Top cuenta: #{row['ranking']} {row['cuenta_nombre']} "
                f"({row['movimientos']:,} mov | {row['monto_total']:,.2f} | {row['participacion_pct']:.4f}%)"
            )
        if mes_actividad:
            print(
                f"  Mes mayor actividad: {mes_actividad['nombre_mes']} {mes_actividad['anio']} "
                f"(#{mes_actividad['ranking_actividad']} | {mes_actividad['movimientos']:,} mov)"
            )

        total_elapsed = time.perf_counter() - started_at
        print_section("Resumen final")
        print(f"  Cliente resumen: {counts['cliente_resumen']:,} registros")
        print(f"  Proveedor resumen: {counts['proveedor_resumen']:,} registros")
        print(f"  Cuenta resumen: {counts['cuenta_resumen']:,} registros")
        print(f"  Mes resumen: {counts['mes_resumen']:,} registros")
        print(f"  Tiempo total de construccion: {total_elapsed:.2f}s")

        if any(total == 0 for total in counts.values()):
            print("")
            print("ERROR: Una o mas tablas resumen quedaron vacias.")
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
