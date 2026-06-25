"""Pruebas de Executive Capability Layer — descubrimiento, soporte y limitaciones."""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.executive_capability_layer import ExecutiveCapabilityLayer
from app.services.human_language_layer import HumanLanguageLayer
from app.services.intent_router import Intent

MANDATORY_CASES: list[tuple[str, str]] = [
    ("¿Qué puedes hacer?", Intent.CAPABILITY_DISCOVERY.value),
    ("¿Qué sabes hacer?", Intent.CAPABILITY_DISCOVERY.value),
    ("¿Para qué sirves?", Intent.CAPABILITY_DISCOVERY.value),
    ("¿Puedes hacer gráficas?", Intent.FEATURE_SUPPORT.value),
    ("¿Puedes hacer dashboards?", Intent.FEATURE_SUPPORT.value),
    ("¿Puedes generar reportes?", Intent.FEATURE_SUPPORT.value),
    ("¿Puedes exportar a Excel?", Intent.FEATURE_SUPPORT.value),
    ("¿Puedes comparar meses?", Intent.FEATURE_SUPPORT.value),
    ("¿Puedes analizar tendencias?", Intent.FEATURE_SUPPORT.value),
    ("¿Puedes detectar anomalías?", Intent.FEATURE_SUPPORT.value),
    ("¿Puedes hacer recomendaciones?", Intent.FEATURE_SUPPORT.value),
    ("¿Puedes hacer predicciones?", Intent.FEATURE_SUPPORT.value),
    ("¿Qué no puedes hacer?", Intent.LIMITATIONS.value),
    ("¿Qué limitaciones tienes?", Intent.LIMITATIONS.value),
    ("¿Qué información no tienes?", Intent.LIMITATIONS.value),
]

EXTRA_CASES: list[tuple[str, str]] = [
    # CAPABILITY_DISCOVERY — tolerancia NLP
    ("Que puedes hacer", Intent.CAPABILITY_DISCOVERY.value),
    ("QUE PUEDES HACER", Intent.CAPABILITY_DISCOVERY.value),
    ("que sabes hacer", Intent.CAPABILITY_DISCOVERY.value),
    ("Como puedes ayudarme", Intent.CAPABILITY_DISCOVERY.value),
    ("¿Cómo puedes ayudarme?", Intent.CAPABILITY_DISCOVERY.value),
    ("Que consultas soportas", Intent.CAPABILITY_DISCOVERY.value),
    ("Que tipo de preguntas respondes", Intent.CAPABILITY_DISCOVERY.value),
    ("Que tipo de analisis realizas", Intent.CAPABILITY_DISCOVERY.value),
    ("Que puedes analizar", Intent.CAPABILITY_DISCOVERY.value),
    ("Con que me puedes ayudar", Intent.CAPABILITY_DISCOVERY.value),
    ("Que informacion puedes consultar", Intent.CAPABILITY_DISCOVERY.value),
    ("Que haces", Intent.CAPABILITY_DISCOVERY.value),
    ("Cuales son tus capacidades", Intent.CAPABILITY_DISCOVERY.value),
    ("Que informacion tienes", Intent.CAPABILITY_DISCOVERY.value),
    ("Que sabes", Intent.CAPABILITY_DISCOVERY.value),
    ("Que datos tienes", Intent.CAPABILITY_DISCOVERY.value),
    # FEATURE_SUPPORT — variantes
    ("puedes hacer graficas", Intent.FEATURE_SUPPORT.value),
    ("Puedes generar graficas", Intent.FEATURE_SUPPORT.value),
    ("puedes exportar informacion", Intent.FEATURE_SUPPORT.value),
    ("puedes comparar anos", Intent.FEATURE_SUPPORT.value),
    ("puedes comparar clientes", Intent.FEATURE_SUPPORT.value),
    ("puedes encontrar riesgos", Intent.FEATURE_SUPPORT.value),
    ("puedes encontrar oportunidades", Intent.FEATURE_SUPPORT.value),
    ("puedes hacer forecasting", Intent.FEATURE_SUPPORT.value),
    ("puedes hacer proyecciones", Intent.FEATURE_SUPPORT.value),
    # LIMITATIONS
    ("que no sabes", Intent.LIMITATIONS.value),
    ("que datos te faltan", Intent.LIMITATIONS.value),
    ("que temas no conoces", Intent.LIMITATIONS.value),
    ("cual es tu alcance", Intent.LIMITATIONS.value),
    ("que no puedes responder", Intent.LIMITATIONS.value),
]

OUT_OF_SCOPE_CASES: list[tuple[str, str | None]] = [
    ("Quien es nuestro mejor cliente", None),
    ("Que paso en junio", None),
    ("Hola", None),
]

CASES = MANDATORY_CASES + EXTRA_CASES


@dataclass
class TestResult:
    question: str
    expected_intent: str
    detected_intent: str | None
    passed: bool
    elapsed_ms: float
    answer_preview: str


def run_case(
    question: str,
    expected_intent: str,
    hll: HumanLanguageLayer,
    layer: ExecutiveCapabilityLayer,
) -> TestResult:
    started = time.perf_counter()
    hl = hll.process(question)
    match = layer.process(hl.original_question, alternate_text=hl.normalized_question)
    elapsed_ms = (time.perf_counter() - started) * 1000
    detected = match.intent.value if match else None
    passed = detected == expected_intent
    preview = match.answer.split("\n")[0] if match else ""
    return TestResult(
        question=question,
        expected_intent=expected_intent,
        detected_intent=detected,
        passed=passed,
        elapsed_ms=elapsed_ms,
        answer_preview=preview,
    )


def main() -> int:
    hll = HumanLanguageLayer()
    layer = ExecutiveCapabilityLayer()
    results: list[TestResult] = []

    print("Executive Capability Layer — batería de pruebas\n")

    for question, expected_intent in CASES:
        result = run_case(question, expected_intent, hll, layer)
        results.append(result)
        status = "OK" if result.passed else "FAIL"
        print(f"[{status}] {question!r}")
        print(f"       intent     : {result.detected_intent} (esperado: {expected_intent})")
        print(f"       tiempo     : {result.elapsed_ms:.2f} ms")
        if result.answer_preview:
            print(f"       respuesta  : {result.answer_preview}...")
        print()

    negative_passed = 0
    print("Casos fuera de alcance (deben retornar None):\n")
    for question, _ in OUT_OF_SCOPE_CASES:
        hl = hll.process(question)
        match = layer.process(hl.original_question, alternate_text=hl.normalized_question)
        ok = match is None
        negative_passed += int(ok)
        status = "OK" if ok else "FAIL"
        detected = match.intent.value if match else "NONE"
        print(f"[{status}] {question!r} -> {detected}")

    total_positive = len(results)
    passed_positive = sum(1 for r in results if r.passed)
    coverage = (passed_positive / total_positive) * 100 if total_positive else 0.0
    avg_ms = sum(r.elapsed_ms for r in results) / total_positive if total_positive else 0.0

    failed = [r for r in results if not r.passed]

    print()
    print(f"Resultado positivo : {passed_positive}/{total_positive} ({coverage:.1f}%)")
    print(f"Resultado negativo : {negative_passed}/{len(OUT_OF_SCOPE_CASES)}")
    print(f"Tiempo promedio    : {avg_ms:.2f} ms")

    if failed:
        print("\nPreguntas no cubiertas en esta batería:")
        for item in failed:
            print(f"  - {item.question!r} (esperado: {item.expected_intent}, detectado: {item.detected_intent})")

    if coverage < 95.0:
        print(f"\nCobertura {coverage:.1f}% por debajo del mínimo 95%.")
        return 1

    if negative_passed != len(OUT_OF_SCOPE_CASES):
        return 1

    print("\nCobertura objetivo alcanzada (>=95%).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
