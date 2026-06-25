"""Pruebas de la capa TOKEN_OPTIMIZATION — demostración ejecutiva determinística."""

import json
import time

from app.services.human_language_layer import HumanLanguageLayer
from app.services.intent_router import Intent
from app.services.token_optimization_layer import TokenOptimizationLayer

CASES: list[str] = [
    "Como optimizas el consumo de tokens?",
    "Por que no envias todo al LLM?",
    "Por que tienes capas intermedias?",
    "Como reduces costos?",
]


def main() -> None:
    hll = HumanLanguageLayer()
    layer = TokenOptimizationLayer()
    passed = 0
    timings: list[float] = []
    last_demo: dict | None = None

    print("TOKEN_OPTIMIZATION — casos de prueba\n")

    for question in CASES:
        started = time.perf_counter()
        hl = hll.process(question)
        match = layer.process(hl.original_question, alternate_text=hl.normalized_question)
        elapsed_ms = (time.perf_counter() - started) * 1000
        timings.append(elapsed_ms)

        ok = (
            match is not None
            and match.intent == Intent.TOKEN_OPTIMIZATION
            and match.confidence == 1.0
            and match.demo is not None
        )
        status = "OK" if ok else "FAIL"
        passed += int(ok)

        detected = match.intent.value if match else "NONE"
        print(f"[{status}] {question!r}")
        print(f"       intent     : {detected}")
        print(f"       confidence : {match.confidence if match else 0.0:.2f}")
        print(f"       tiempo     : {elapsed_ms:.2f} ms")
        if match:
            last_demo = match.demo.model_dump()
        print()

    total = len(CASES)
    avg_ms = sum(timings) / len(timings) if timings else 0.0
    layer_only = []
    for question in CASES:
        t0 = time.perf_counter()
        layer.process(question)
        layer_only.append((time.perf_counter() - t0) * 1000)
    avg_layer_ms = sum(layer_only) / len(layer_only) if layer_only else 0.0

    print(f"Resultado: {passed}/{total} casos exitosos")
    print(f"Tiempo promedio (HLL + capa): {avg_ms:.2f} ms")
    print(f"Tiempo promedio (solo capa): {avg_layer_ms:.3f} ms")

    if last_demo:
        print("\ntoken_optimization_demo (ultimo caso):")
        print(json.dumps(last_demo, ensure_ascii=False, indent=2))

    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
