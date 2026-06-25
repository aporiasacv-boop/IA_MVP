"""Pruebas de intenciones empresariales ampliadas — HLL + Intent Router."""

import time

from app.services.human_language_layer import HumanLanguageLayer
from app.services.intent_router import Intent, IntentRouter

CASES: list[tuple[str, str, float]] = [
    ("Cual es nuestro peor cliente?", Intent.BOTTOM_CLIENTES.value, 0.94),
    ("Quien nos compra menos?", Intent.BOTTOM_CLIENTES.value, 0.94),
    ("Cual fue el peor mes?", Intent.WORST_MONTH.value, 0.94),
    ("Cual fue el mejor mes?", Intent.BEST_MONTH.value, 0.94),
    ("Que cliente crecio mas?", Intent.CLIENTE_CRECIMIENTO.value, 0.94),
    ("Que proveedor cayo mas?", Intent.PROVEEDOR_CAIDA.value, 0.94),
    ("Haz un resumen ejecutivo del 2025", Intent.EXECUTIVE_SUMMARY.value, 0.94),
    ("Que riesgos detectas?", Intent.RISKS.value, 1.0),
    ("Que oportunidades observas?", Intent.OPPORTUNITIES.value, 0.94),
]

NEW_INTENTS = (
    Intent.BOTTOM_CLIENTES,
    Intent.BOTTOM_PROVEEDORES,
    Intent.BOTTOM_CUENTAS,
    Intent.BEST_MONTH,
    Intent.WORST_MONTH,
    Intent.CLIENTE_CRECIMIENTO,
    Intent.CLIENTE_CAIDA,
    Intent.PROVEEDOR_CRECIMIENTO,
    Intent.PROVEEDOR_CAIDA,
    Intent.EXECUTIVE_SUMMARY,
    Intent.RISKS,
    Intent.OPPORTUNITIES,
)


def main() -> None:
    hll = HumanLanguageLayer()
    router = IntentRouter()
    passed = 0
    timings: list[float] = []
    coverage: dict[str, int] = {intent.value: 0 for intent in NEW_INTENTS}

    print("Intenciones empresariales ampliadas — casos de prueba\n")

    for question, expected_intent, min_confidence in CASES:
        started = time.perf_counter()
        hl = hll.process(question)
        match = router.route(
            hl.normalized_question,
            corrections_applied=hl.corrections_applied,
            intent_hint=hl.intent_hint,
        )
        elapsed_ms = (time.perf_counter() - started) * 1000
        timings.append(elapsed_ms)

        ok = (
            match.intent.value == expected_intent
            and match.confidence >= min_confidence
        )
        status = "OK" if ok else "FAIL"
        passed += int(ok)
        if ok:
            coverage[expected_intent] = coverage.get(expected_intent, 0) + 1

        print(f"[{status}] {question!r}")
        print(f"       normalizada : {hl.normalized_question!r}")
        print(f"       intent      : {match.intent.value} (esperado: {expected_intent})")
        print(f"       confidence  : {match.confidence:.2f} ({match.match_type})")
        print(f"       tiempo      : {elapsed_ms:.2f} ms")
        print()

    total = len(CASES)
    avg_ms = sum(timings) / len(timings) if timings else 0.0
    intents_covered = sum(1 for count in coverage.values() if count > 0)

    print("=" * 60)
    print(f"Resultado: {passed}/{total} casos exitosos")
    print(f"Tiempo promedio: {avg_ms:.2f} ms")
    print(f"Intenciones nuevas cubiertas en pruebas: {intents_covered}/{len(NEW_INTENTS)}")
    print("\nCobertura por intencion:")
    for intent in NEW_INTENTS:
        count = coverage.get(intent.value, 0)
        mark = "OK" if count else "--"
        print(f"  [{mark}] {intent.value}: {count} caso(s)")

    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
