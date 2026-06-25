from __future__ import annotations

import sys
import time
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

BASE_URL = "http://127.0.0.1:8001"

TEST_CASES = [
    ("¿Qué pasó en junio?", "MONTH_ANALYSIS"),
    ("Resume 2025.", "YEAR_SUMMARY"),
    ("¿Qué hallazgos detectaste?", "EXECUTIVE_INSIGHTS"),
    ("¿Dónde está concentrado el negocio?", "BUSINESS_CONCENTRATION"),
]


def truncate(text: str, limit: int = 360) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "..."


def main() -> int:
    print("=" * 80)
    print("TEST EXECUTIVE CHAT - IA_MVP")
    print(f"Base URL: {BASE_URL}")
    print("=" * 80)

    errors = 0

    with httpx.Client(base_url=BASE_URL, timeout=120.0) as client:
        try:
            health = client.get("/health")
            if health.status_code != 200:
                print("[FAIL] Servidor no disponible en /health")
                return 1
        except httpx.ConnectError:
            print("[FAIL] No se pudo conectar. Ejecuta: uvicorn app.main:app --reload --port 8001")
            return 1

        for question, expected_intent in TEST_CASES:
            started = time.perf_counter()
            response = client.post("/api/chat", json={"question": question})
            elapsed_ms = (time.perf_counter() - started) * 1000

            print("")
            print(f"Pregunta: {question}")
            print(f"  HTTP: {response.status_code}")
            print(f"  Tiempo total: {elapsed_ms:.2f} ms")

            if response.status_code != 200:
                print(f"  [FAIL] {response.text[:200]}")
                errors += 1
                continue

            payload = response.json()
            intent = payload.get("intent")
            answer = payload.get("answer", "")
            sources = payload.get("sources", [])
            data = payload.get("data")

            print(f"  Intencion detectada: {intent}")
            print(f"  Intencion esperada:  {expected_intent}")
            print(f"  Fuentes utilizadas: {', '.join(sources) if sources else '(ninguna)'}")
            print(f"  Respuesta generada: {truncate(answer)}")

            if intent != expected_intent:
                print("  [FAIL] Intencion incorrecta")
                errors += 1
                continue

            if not sources:
                print("  [FAIL] Se esperaban fuentes consolidadas")
                errors += 1
                continue

            if not answer:
                print("  [FAIL] Falta answer")
                errors += 1
                continue

            if data is None:
                print("  [FAIL] Falta data")
                errors += 1
                continue

            if "periodo" not in answer.lower() and "2025" not in answer:
                print("  [WARN] La respuesta no menciona explicitamente el periodo")

            print("  [OK]")

    print("")
    print("=" * 80)
    if errors:
        print(f"[FAIL] {errors} pregunta(s) con error")
        return 1
    print("[OK] Preguntas ejecutivas respondidas correctamente")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
