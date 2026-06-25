from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database.database import SessionLocal
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.executive_summary_repository import ExecutiveSummaryRepository


def print_section(title: str) -> None:
    print("")
    print("=" * 72)
    print(title)
    print("=" * 72)


def compare_entity(
    label: str,
    kpi_row: dict,
    summary_row: dict,
    code_key: str,
    name_key: str,
    kpi_mov_key: str,
    kpi_monto_key: str,
) -> bool:
    kpi_code = kpi_row[code_key]
    kpi_name = kpi_row[name_key]
    kpi_mov = kpi_row[kpi_mov_key]
    kpi_monto = kpi_row[kpi_monto_key]
    summary_code = summary_row[code_key]
    summary_name = summary_row[name_key]
    summary_mov = summary_row["movimientos"]
    summary_monto = summary_row["monto_total"]

    ok = (
        kpi_code == summary_code
        and kpi_name == summary_name
        and kpi_mov == summary_mov
        and Decimal(kpi_monto) == Decimal(summary_monto)
    )

    status = "OK" if ok else "FAIL"
    print(f"  [{status}] Top {label.lower()}")
    print(f"    KPI ejecutivo : {kpi_code} | {kpi_name} | mov={kpi_mov:,} | monto={Decimal(kpi_monto):,.2f}")
    print(
        f"    Resumen capa  : {summary_code} | {summary_name} | "
        f"mov={summary_mov:,} | monto={Decimal(summary_monto):,.2f}"
    )
    return ok


def main() -> int:
    print("Validando capa de resumenes ejecutivos contra KPIs ejecutivos...")

    with SessionLocal() as session:
        analytics_repo = AnalyticsRepository(session)
        summary_repo = ExecutiveSummaryRepository(session)

        kpis = analytics_repo.fetch_kpis_ejecutivos()
        top_cliente = summary_repo.obtener_top_clientes_resumen(1)
        top_proveedor = summary_repo.obtener_top_proveedores_resumen(1)
        top_cuenta = summary_repo.obtener_cuenta_resumen()[:1]
        meses = summary_repo.obtener_mes_resumen()

        if not top_cliente or not top_proveedor or not top_cuenta or not meses:
            print("ERROR: Faltan datos en tablas resumen. Ejecute scripts/build_executive_summaries.py primero.")
            return 1

        print_section("Validacion top entidades")
        checks = [
            compare_entity(
                "Cliente",
                kpis,
                top_cliente[0],
                "cliente_codigo",
                "cliente_nombre",
                "cliente_movimientos",
                "cliente_monto_total",
            ),
            compare_entity(
                "Proveedor",
                kpis,
                top_proveedor[0],
                "proveedor_codigo",
                "proveedor_nombre",
                "proveedor_movimientos",
                "proveedor_monto_total",
            ),
            compare_entity(
                "Cuenta",
                kpis,
                top_cuenta[0],
                "cuenta_codigo",
                "cuenta_nombre",
                "cuenta_movimientos",
                "cuenta_monto_total",
            ),
        ]

        print_section("Validacion mes mayor actividad")
        mes_resumen = next(row for row in meses if row["ranking_actividad"] == 1)
        mes_ok = (
            mes_resumen["anio"] == kpis["actividad_anio"]
            and mes_resumen["mes"] == kpis["actividad_mes"]
            and mes_resumen["movimientos"] == kpis["actividad_movimientos"]
        )
        mes_status = "OK" if mes_ok else "FAIL"
        print(f"  [{mes_status}] Mes mayor actividad")
        print(
            f"    KPI ejecutivo : {kpis['actividad_anio']}-{kpis['actividad_mes']:02d} | "
            f"mov={kpis['actividad_movimientos']:,}"
        )
        print(
            f"    Resumen capa  : {mes_resumen['anio']}-{mes_resumen['mes']:02d} | "
            f"{mes_resumen['nombre_mes']} | mov={mes_resumen['movimientos']:,}"
        )
        checks.append(mes_ok)

        print_section("Validacion mes mayor volumen")
        mes_volumen = next(row for row in meses if row["ranking_volumen"] == 1)
        volumen_ok = (
            mes_volumen["anio"] == kpis["volumen_anio"]
            and mes_volumen["mes"] == kpis["volumen_mes"]
            and Decimal(mes_volumen["monto_total"]) == Decimal(kpis["volumen_mes_total"])
        )
        volumen_status = "OK" if volumen_ok else "FAIL"
        print(f"  [{volumen_status}] Mes mayor volumen")
        print(
            f"    KPI ejecutivo : {kpis['volumen_anio']}-{kpis['volumen_mes']:02d} | "
            f"monto={Decimal(kpis['volumen_mes_total']):,.2f}"
        )
        print(
            f"    Resumen capa  : {mes_volumen['anio']}-{mes_volumen['mes']:02d} | "
            f"{mes_volumen['nombre_mes']} | monto={Decimal(mes_volumen['monto_total']):,.2f}"
        )
        checks.append(volumen_ok)

        print_section("Resultado final")
        passed = sum(checks)
        total = len(checks)
        print(f"  Validaciones exitosas: {passed}/{total}")
        if all(checks):
            print("  Estado: VALIDACION COMPLETA OK")
            return 0

        print("  Estado: VALIDACION CON DISCREPANCIAS")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
