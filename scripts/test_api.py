from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import httpx

BASE_URL = "http://127.0.0.1:8001"

NEW_INSIGHT_TYPES = {
    "cliente_mayor_crecimiento",
    "proveedor_mayor_crecimiento",
    "cuenta_mayor_crecimiento",
    "mes_atipico",
}

INSIGHTS_MAX_MS = 50.0

ENDPOINTS = [
    ("GET", "/api/kpis", None),
    ("GET", "/api/kpis/ejecutivos", None),
    ("GET", "/api/top-clientes?limit=10", None),
    ("GET", "/api/top-proveedores?limit=10", None),
    ("GET", "/api/top-cuentas?limit=10", None),
    ("GET", "/api/resumen-mensual", None),
    ("GET", "/api/evolucion-cliente/C0027", None),
    ("GET", "/api/evolucion-proveedor/20401001", None),
    ("GET", "/api/evolucion-cuenta/20603001", None),
    ("GET", "/api/insights", None),
    ("GET", "/api/insights/resumen", None),
    ("GET", "/api/evolucion-cliente/INVALIDO", None),
]


def format_bytes(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    return f"{size / 1024:.2f} KB"


def print_insights_detail(data: list) -> None:
    print(f"  Cantidad de insights: {len(data)}")
    tipos = {item.get("tipo") for item in data}
    nuevos = tipos & NEW_INSIGHT_TYPES
    print(f"  Nuevos insights detectados: {len(nuevos)}/{len(NEW_INSIGHT_TYPES)}")
    for tipo in sorted(NEW_INSIGHT_TYPES):
        estado = "OK" if tipo in tipos else "FALTA"
        print(f"    [{estado}] {tipo}")
    for item in data:
        print(f"    - [{item.get('severidad', '?')}] {item.get('tipo', '?')}: {item.get('mensaje', '')}")


def print_insights_resumen_detail(data: dict) -> None:
    print(f"  Total insights: {data.get('total_insights', 0)}")
    print(
        f"  Severidades: criticos={data.get('criticos', 0)}, "
        f"altos={data.get('altos', 0)}, medios={data.get('medios', 0)}, "
        f"bajos={data.get('bajos', 0)}"
    )


def main() -> int:
    print("=" * 80)
    print("TEST API ANALITICA - IA_MVP")
    print(f"Base URL: {BASE_URL}")
    print("=" * 80)

    errors = 0

    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        try:
            health = client.get("/health")
            if health.status_code != 200:
                print("[FAIL] Servidor no disponible en /health")
                return 1
        except httpx.ConnectError:
            print("[FAIL] No se pudo conectar. Ejecuta: uvicorn app.main:app --reload --port 8001")
            return 1

        for method, path, body in ENDPOINTS:
            started = time.perf_counter()
            response = client.request(method, path, json=body)
            elapsed_ms = (time.perf_counter() - started) * 1000
            payload_size = len(response.content)
            status = response.status_code

            print("")
            print(f"{method} {path}")
            print(f"  HTTP: {status}")
            print(f"  Tiempo: {elapsed_ms:.2f} ms")
            print(f"  Payload: {format_bytes(payload_size)}")

            if path.endswith("/INVALIDO"):
                if status != 404:
                    print("  [FAIL] Se esperaba HTTP 404")
                    errors += 1
                else:
                    print("  [OK] Error esperado para codigo invalido")
                continue

            if status != 200:
                print(f"  [FAIL] {response.text[:200]}")
                errors += 1
                continue

            try:
                data = response.json()
            except json.JSONDecodeError:
                print("  [FAIL] Respuesta no es JSON valido")
                errors += 1
                continue

            if path == "/api/insights" and isinstance(data, list):
                print_insights_detail(data)
                if len(data) <= 10:
                    print("  [FAIL] Se esperaban mas de 10 insights")
                    errors += 1
                if elapsed_ms > INSIGHTS_MAX_MS:
                    print(f"  [FAIL] Tiempo excede {INSIGHTS_MAX_MS} ms")
                    errors += 1
                tipos = {item.get("tipo") for item in data}
                if not NEW_INSIGHT_TYPES.issubset(tipos):
                    print("  [FAIL] Faltan insights de tendencias/anomalias")
                    errors += 1
                preview = json.dumps(data, ensure_ascii=False)
                if len(preview) > 500:
                    preview = preview[:500] + "..."
                print(f"  Payload JSON: {preview}")
            elif path == "/api/insights/resumen" and isinstance(data, dict):
                print_insights_resumen_detail(data)
                if data.get("total_insights", 0) <= 10:
                    print("  [FAIL] total_insights debe ser mayor a 10")
                    errors += 1
                if elapsed_ms > INSIGHTS_MAX_MS:
                    print(f"  [FAIL] Tiempo excede {INSIGHTS_MAX_MS} ms")
                    errors += 1
                preview = json.dumps(data, ensure_ascii=False)
                print(f"  Payload JSON: {preview}")
            else:
                preview = json.dumps(data, ensure_ascii=False)
                if len(preview) > 180:
                    preview = preview[:180] + "..."
                print(f"  Respuesta: {preview}")
            print("  [OK]")

    print("")
    print("=" * 80)
    if errors:
        print(f"[FAIL] {errors} endpoint(s) con error")
        return 1
    print("[OK] Todos los endpoints respondieron correctamente")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
