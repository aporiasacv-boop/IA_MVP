from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database.database import SessionLocal
from app.repositories.metadata_repository import MetadataRepository
from app.services.metadata_service import MetadataService
from app.services.prompt_audit import PromptAudit
from app.services.prompt_builder import PromptBuilder
from app.services.query_executor import QueryExecutor
from app.services.analytics_service import AnalyticsService
from app.services.insights_engine import InsightsEngine
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.insights_repository import InsightsRepository
from app.services.intent_router import Intent, IntentRouter

BASE_URL = "http://127.0.0.1:8001"
QUESTION = "¿Quién es nuestro mejor cliente?"


def pct_reduction(before: float, after: float) -> float:
    if before <= 0:
        return 0.0
    return round(((before - after) / before) * 100, 2)


def estimate_baseline_prompt(question: str, intent: str, data: object) -> dict:
    session = SessionLocal()
    try:
        metadata_service = MetadataService(MetadataRepository(session))
        builder = PromptBuilder()
        dataset_context = metadata_service.get_prompt_context()
        prompt, context_chars = builder.build(
            question,
            intent,
            data,
            dataset_context=dataset_context,
            temporal_context=(
                "Referencia temporal: periodo completo del dataset "
                f"({metadata_service.get_dataset_summary()['fecha_minima']} a "
                f"{metadata_service.get_dataset_summary()['fecha_maxima']})."
            ),
            sources=[intent],
        )
        audit = PromptAudit.analyze(
            question=question,
            prompt=prompt,
            context_chars=context_chars,
            sources_used=[intent, "METADATA"],
        )
        return audit.metrics.model_dump()
    finally:
        session.close()


def fetch_query_data(question: str) -> tuple[str, object]:
    router = IntentRouter()
    match = router.route(question)
    session = SessionLocal()
    try:
        executor = QueryExecutor(
            AnalyticsService(AnalyticsRepository(session)),
            InsightsEngine(InsightsRepository(session)),
        )
        data = executor.execute(match)
        return match.intent.value, data
    finally:
        session.close()


def print_metrics(label: str, metrics: dict, llm_ms: float | None = None) -> None:
    print(f"  {label}")
    print(f"    prompt_chars: {metrics.get('prompt_chars', 0)}")
    print(f"    context_chars: {metrics.get('context_chars', 0)}")
    print(f"    estimated_tokens: {metrics.get('estimated_tokens', 0)}")
    print(f"    sources_used: {', '.join(metrics.get('sources_used', []))}")
    if llm_ms is not None:
        print(f"    llm_ms: {llm_ms:.2f}")


def main() -> int:
    print("=" * 80)
    print("TEST PROMPT AUDIT - IA_MVP")
    print(f"Pregunta: {QUESTION}")
    print("=" * 80)

    intent, data = fetch_query_data(QUESTION)
    before = estimate_baseline_prompt(QUESTION, intent, data)

    print("")
    print("ANTES (contexto completo sin optimizar)")
    print_metrics("Baseline", before)

    with httpx.Client(base_url=BASE_URL, timeout=120.0) as client:
        try:
            health = client.get("/health")
            if health.status_code != 200:
                print("[FAIL] Servidor no disponible")
                return 1
        except httpx.ConnectError:
            print("[FAIL] Ejecuta: uvicorn app.main:app --port 8001")
            return 1

        started = time.perf_counter()
        response = client.post("/api/chat", json={"question": QUESTION})
        elapsed_ms = (time.perf_counter() - started) * 1000

        if response.status_code != 200:
            print(f"[FAIL] HTTP {response.status_code}: {response.text[:200]}")
            return 1

        payload = response.json()
        after = payload.get("prompt_metrics", {})
        timings = payload.get("timings", {})
        llm_ms = timings.get("llm_ms", elapsed_ms)

    print("")
    print("DESPUES (contexto optimizado)")
    print_metrics("Optimizado", after, llm_ms=llm_ms)

    reduction_chars = pct_reduction(before["prompt_chars"], after.get("prompt_chars", 0))
    reduction_tokens = pct_reduction(
        before["estimated_tokens"],
        after.get("estimated_tokens", 0),
    )

    print("")
    print("REDUCCION")
    print(f"  prompt_chars: {reduction_chars}%")
    print(f"  estimated_tokens: {reduction_tokens}%")

    errors = 0
    if payload.get("intent") != Intent.TOP_CLIENTES.value:
        print("[FAIL] Intencion esperada TOP_CLIENTES")
        errors += 1
    if not after:
        print("[FAIL] Falta prompt_metrics en la respuesta")
        errors += 1
    if reduction_chars < 50:
        print(f"[FAIL] Reduccion de prompt_chars {reduction_chars}% < 50%")
        errors += 1

    print("")
    print("=" * 80)
    if errors:
        print(f"[FAIL] {errors} validacion(es) con error")
        return 1
    print("[OK] Prompt audit y optimizacion validados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
