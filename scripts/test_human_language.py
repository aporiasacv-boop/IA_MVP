"""Prueba determinística de Human Language Layer + Intent Router."""

from app.services.human_language_layer import HumanLanguageLayer
from app.services.intent_router import IntentRouter

CASES: list[tuple[str, str]] = [
    ("Que informasion tienes", "CAPABILITY_DISCOVERY"),
    ("Que sabes", "CAPABILITY_DISCOVERY"),
    ("Quien es el clinte mas fuerte", "TOP_CLIENTES"),
    ("Que paso en juno", "MONTH_ANALYSIS"),
    ("Que puedes responder", "CAPABILITY_DISCOVERY"),
]


def main() -> None:
    hll = HumanLanguageLayer()
    router = IntentRouter()
    passed = 0

    print("Human Language Layer — casos de prueba\n")

    for question, expected_intent in CASES:
        result = hll.process(question)
        match = router.route(result.normalized_question)
        ok = match.intent.value == expected_intent
        status = "OK" if ok else "FAIL"
        passed += int(ok)

        print(f"[{status}] {question!r}")
        print(f"       normalized: {result.normalized_question!r}")
        if result.corrections_applied:
            print(f"       corrections: {result.corrections_applied}")
        print(f"       intent: {match.intent.value} (esperado: {expected_intent})")
        print()

    total = len(CASES)
    print(f"Resultado: {passed}/{total} casos exitosos")
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
