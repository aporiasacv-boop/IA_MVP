"""Pruebas de EntityExtractionLayer — extracción determinística de entidades."""

import time

from app.services.entity_extraction_layer import EntityExtractionLayer
from app.services.human_language_layer import HumanLanguageLayer
from app.services.intent_router import Intent, IntentRouter

CASES: list[tuple[str, dict, str | None]] = [
    ("Resume junio", {"month": 6}, Intent.MONTH_ANALYSIS.value),
    (
        "Que paso en agosto de 2025?",
        {"month": 8, "year": 2025},
        Intent.MONTH_ANALYSIS.value,
    ),
    ("Analiza diciembre", {"month": 12}, Intent.MONTH_ANALYSIS.value),
    ("Hablame del cliente C0003", {"client_code": "C0003"}, None),
    ("Revisa la cuenta 20603001", {"account_code": "20603001"}, None),
    ("Resumen del ultimo ano", {"period": "last_year"}, None),
]


def main() -> None:
    hll = HumanLanguageLayer()
    extractor = EntityExtractionLayer()
    router = IntentRouter()
    passed = 0
    timings: list[float] = []
    layer_only: list[float] = []

    print("Entity Extraction Layer — casos de prueba\n")

    for question, expected_fields, expected_intent in CASES:
        started = time.perf_counter()
        hl = hll.process(question)
        entities = extractor.extract(
            hl.normalized_question,
            alternate_text=hl.original_question,
        )
        match = router.route(
            hl.normalized_question,
            corrections_applied=hl.corrections_applied,
            intent_hint=hl.intent_hint,
        )
        elapsed_ms = (time.perf_counter() - started) * 1000
        timings.append(elapsed_ms)

        t0 = time.perf_counter()
        extractor.extract(question)
        layer_only.append((time.perf_counter() - t0) * 1000)

        entity_dict = entities.model_dump()
        fields_ok = all(entity_dict.get(key) == value for key, value in expected_fields.items())
        intent_ok = expected_intent is None or match.intent.value == expected_intent
        ok = fields_ok and intent_ok
        status = "OK" if ok else "FAIL"
        passed += int(ok)

        print(f"[{status}] {question!r}")
        print(f"       normalizada : {hl.normalized_question!r}")
        print(f"       entities    : {entity_dict}")
        if expected_intent:
            print(f"       intent      : {match.intent.value} (esperado: {expected_intent})")
        print(f"       tiempo      : {elapsed_ms:.2f} ms")
        if not fields_ok:
            print(f"       esperado    : {expected_fields}")
        print()

    total = len(CASES)
    avg_ms = sum(timings) / len(timings) if timings else 0.0
    avg_layer_ms = sum(layer_only) / len(layer_only) if layer_only else 0.0

    print("=" * 60)
    print(f"Resultado: {passed}/{total} casos exitosos")
    print(f"Tiempo promedio (HLL + extraccion): {avg_ms:.2f} ms")
    print(f"Tiempo promedio (solo extraccion): {avg_layer_ms:.3f} ms")

    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
