from __future__ import annotations

import json
import sys
import time

import httpx

BASE_URL = "http://127.0.0.1:8001"

TEST_QUESTIONS: list[tuple[str, str]] = [
    ("¿Quién es nuestro mejor cliente?", "TOP_CLIENTES"),
    ("¿Cuál es el proveedor principal?", "TOP_PROVEEDORES"),
    ("Dame los insights.", "INSIGHTS"),
    ("Resume los meses.", "RESUMEN_MENSUAL"),
    ("Muéstrame los KPIs.", "KPIS"),
]


def format_preview(data: object) -> str:
    preview = json.dumps(data, ensure_ascii=False)
    if len(preview) > 220:
        return preview[:220] + "..."
    return preview


def main() -> int:
    print("=" * 80)
    print("TEST INTENT ROUTER - IA_MVP")
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

        for question, expected_intent in TEST_QUESTIONS:
            started = time.perf_counter()
            response = client.post("/api/chat", json={"question": question})
            elapsed_ms = (time.perf_counter() - started) * 1000

            print("")
            print(f"Pregunta: {question}")
            print(f"  HTTP: {response.status_code}")
            print(f"  Tiempo: {elapsed_ms:.2f} ms")

            if response.status_code != 200:
                print(f"  [FAIL] {response.text[:200]}")
                errors += 1
                continue

            payload = response.json()
            intent = payload.get("intent")
            data = payload.get("data")

            print(f"  Intencion detectada: {intent}")
            print(f"  Intencion esperada:  {expected_intent}")

            if intent != expected_intent:
                print("  [FAIL] Intencion incorrecta")
                errors += 1
                continue

            if data is None:
                print("  [FAIL] data vacio")
                errors += 1
                continue

            if isinstance(data, list):
                print(f"  Registros devueltos: {len(data)}")
            elif isinstance(data, dict):
                print(f"  Campos devueltos: {len(data)}")

            print(f"  Resultado: {format_preview(data)}")
            print("  [OK]")

    print("")
    print("=" * 80)
    if errors:
        print(f"[FAIL] {errors} pregunta(s) con error")
        return 1
    print("[OK] Todas las preguntas se clasificaron correctamente")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
