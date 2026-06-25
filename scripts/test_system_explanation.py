"""Pruebas de System Explanation Layer — respuestas ejecutivas determinísticas."""

import time

from app.services.human_language_layer import HumanLanguageLayer
from app.services.intent_router import Intent
from app.services.system_explanation_layer import SystemExplanationLayer

CASES: list[tuple[str, str]] = [
    ("Como funcionas?", Intent.SYSTEM_EXPLANATION.value),
    ("Como trabajas?", Intent.SYSTEM_EXPLANATION.value),
    ("De donde salen los datos?", Intent.DATA_SOURCE.value),
    ("Como generas las respuestas?", Intent.SYSTEM_EXPLANATION.value),
    ("Como sabes eso?", Intent.SYSTEM_EXPLANATION.value),
    ("Usas inteligencia artificial para todo?", Intent.SYSTEM_EXPLANATION.value),
]


def main() -> None:
    hll = HumanLanguageLayer()
    layer = SystemExplanationLayer()
    passed = 0
    timings: list[float] = []
    layer_only: list[float] = []

    print("System Explanation Layer — casos de prueba\n")

    for question, expected_intent in CASES:
        started = time.perf_counter()
        hl = hll.process(question)
        match = layer.process(hl.original_question, alternate_text=hl.normalized_question)
        elapsed_ms = (time.perf_counter() - started) * 1000
        timings.append(elapsed_ms)

        t0 = time.perf_counter()
        layer.process(question)
        layer_only.append((time.perf_counter() - t0) * 1000)

        ok = (
            match is not None
            and match.intent.value == expected_intent
            and match.confidence == 1.0
        )
        status = "OK" if ok else "FAIL"
        passed += int(ok)

        detected = match.intent.value if match else "NONE"
        print(f"[{status}] {question!r}")
        print(f"       intent     : {detected} (esperado: {expected_intent})")
        print(f"       confidence : {match.confidence if match else 0.0:.2f}")
        print(f"       tipo       : {match.match_type if match else '-'}")
        print(f"       tiempo     : {elapsed_ms:.2f} ms")
        if match and ok:
            preview = match.answer.split("\n")[0]
            print(f"       respuesta  : {preview}...")
        print()

    total = len(CASES)
    avg_ms = sum(timings) / len(timings) if timings else 0.0
    avg_layer_ms = sum(layer_only) / len(layer_only) if layer_only else 0.0

    print(f"Resultado: {passed}/{total} casos exitosos")
    print(f"Tiempo promedio (HLL + capa): {avg_ms:.2f} ms")
    print(f"Tiempo promedio (solo capa): {avg_layer_ms:.3f} ms")

    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
