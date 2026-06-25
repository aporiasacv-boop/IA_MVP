from __future__ import annotations

import sys
import time

import httpx

BASE_URL = "http://127.0.0.1:8001"

TEST_QUESTIONS = [
    "¿Quién es nuestro mejor cliente?",
    "¿Cuál es el proveedor principal?",
    "Dame los insights.",
    "Resume los meses.",
]


def truncate(text: str, limit: int = 320) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "..."


def print_timings(timings: dict) -> None:
    print(f"  Intent: {timings.get('_intent', '')}")
    print(f"  Router: {timings.get('router_ms', 0)} ms")
    print(f"  Query: {timings.get('query_ms', 0)} ms")
    print(f"  Context: {timings.get('context_ms', 0)} ms")
    print(f"  Prompt: {timings.get('prompt_ms', 0)} ms")
    print(f"  LLM: {timings.get('llm_ms', 0)} ms")
    print(f"  Total: {timings.get('total_ms', 0)} ms")


def main() -> int:
    print("=" * 80)
    print("TEST CHAT CON OLLAMA - IA_MVP")
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

        for question in TEST_QUESTIONS:
            started = time.perf_counter()
            response = client.post("/api/chat", json={"question": question})
            elapsed_ms = (time.perf_counter() - started) * 1000

            print("")
            print(f"Pregunta: {question}")
            print(f"  HTTP: {response.status_code}")
            print(f"  Tiempo cliente: {elapsed_ms:.2f} ms")

            if response.status_code != 200:
                print(f"  [FAIL] {response.text[:200]}")
                errors += 1
                continue

            payload = response.json()
            intent = payload.get("intent")
            answer = payload.get("answer", "")
            data = payload.get("data")
            timings = payload.get("timings", {})
            prompt_metrics = payload.get("prompt_metrics", {})

            print(f"  Intent: {intent}")
            print(f"  Router: {timings.get('router_ms', 0)} ms")
            print(f"  Query: {timings.get('query_ms', 0)} ms")
            print(f"  Context: {timings.get('context_ms', 0)} ms")
            print(f"  Prompt: {timings.get('prompt_ms', 0)} ms")
            print(f"  LLM: {timings.get('llm_ms', 0)} ms")
            print(f"  Total: {timings.get('total_ms', 0)} ms")
            print(
                f"  Prompt metrics: chars={prompt_metrics.get('prompt_chars', 0)}, "
                f"tokens~={prompt_metrics.get('estimated_tokens', 0)}, "
                f"sources={prompt_metrics.get('sources_used', [])}"
            )
            print(f"  Respuesta generada: {truncate(answer)}")

            if not intent:
                print("  [FAIL] Falta intent")
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

            required_timing_fields = [
                "router_ms",
                "query_ms",
                "context_ms",
                "prompt_ms",
                "llm_ms",
                "total_ms",
            ]
            if not all(field in timings for field in required_timing_fields):
                print("  [FAIL] Faltan campos en timings")
                errors += 1
                continue

            if "prompt_chars" not in prompt_metrics:
                print("  [FAIL] Faltan prompt_metrics")
                errors += 1
                continue

            print("  [OK]")

    print("")
    print("=" * 80)
    if errors:
        print(f"[FAIL] {errors} pregunta(s) con error")
        return 1
    print("[OK] Chat respondio correctamente en todas las preguntas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
