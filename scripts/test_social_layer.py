"""Pruebas de la Social & Identity Layer — respuestas conversacionales determinísticas."""

import time

from app.services.human_language_layer import HumanLanguageLayer
from app.services.intent_router import Intent
from app.services.social_identity_layer import SocialIdentityLayer

CASES: list[tuple[str, str]] = [
    ("Hola", Intent.GREETING.value),
    ("Hi", Intent.GREETING.value),
    ("Buenos dias", Intent.GREETING.value),
    ("Quien eres", Intent.IDENTITY.value),
    ("Que KPIs tienes", Intent.KPI_CATALOG.value),
    ("Que insights tienes", Intent.INSIGHT_CATALOG.value),
    ("Como estas", Intent.STATUS.value),
    ("Producto mas vendido", Intent.OUT_OF_SCOPE.value),
]


def main() -> None:
    hll = HumanLanguageLayer()
    social_layer = SocialIdentityLayer()
    passed = 0
    timings: list[float] = []

    print("Social & Identity Layer — casos de prueba\n")

    for question, expected_intent in CASES:
        started = time.perf_counter()
        hl = hll.process(question)
        match = social_layer.process(hl.original_question, alternate_text=hl.normalized_question)
        elapsed_ms = (time.perf_counter() - started) * 1000
        timings.append(elapsed_ms)

        ok = match is not None and match.intent.value == expected_intent
        status = "OK" if ok else "FAIL"
        passed += int(ok)

        detected = match.intent.value if match else "NONE"
        confidence = match.confidence if match else 0.0
        print(f"[{status}] {question!r}")
        print(f"       intent     : {detected} (esperado: {expected_intent})")
        print(f"       confidence : {confidence:.2f}")
        print(f"       tiempo     : {elapsed_ms:.2f} ms")
        if match and ok:
            preview = match.answer.split("\n")[0]
            print(f"       respuesta  : {preview}...")
        print()

    total = len(CASES)
    avg_ms = sum(timings) / len(timings) if timings else 0.0
    max_ms = max(timings) if timings else 0.0

    print(f"Resultado: {passed}/{total} casos exitosos")
    print(f"Tiempo promedio (HLL + Social): {avg_ms:.2f} ms")
    print(f"Tiempo maximo: {max_ms:.2f} ms")

    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
