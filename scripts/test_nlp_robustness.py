"""
Batería agresiva de robustez NLP — Human Language Layer + Intent Router.

Valida comprensión determinística (sin LLM) de ortografía, sinónimos,
metaconocimiento, cobertura, lenguaje coloquial y ambigüedad.

Uso:
    python scripts/test_nlp_robustness.py
    python scripts/test_nlp_robustness.py --write-report
    python scripts/test_nlp_robustness.py --min-success 85
"""

from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from app.services.human_language_layer import HumanLanguageLayer
from app.services.intent_router import Intent, IntentRouter

BASELINE_SUCCESS = 64.3
MIN_SUCCESS_DEFAULT = 85.0
IDEAL_SUCCESS = 90.0
REPORT_PATH = Path(__file__).resolve().parent.parent / "docs" / "nlp_robustness_report.md"

PATTERNS_ADDED = [
    "Abreviaciones: q, ke, k, xq, pq, pa → expansión determinística",
    "Correcciones ortográficas: tines, clente, asta, actualisado, hallasgos, conoses",
    "Cobertura temporal: 11 variantes → DATA_COVERAGE",
    "Coloquial clientes: quien compra mas, cliente mas grande, quien nos compra mas",
    "Coloquial proveedores: quien vende mas, quien nos vende mas",
    "Concentración: donde esta el negocio, quien mueve mas dinero, mayor actividad",
    "Insights ejecutivos: que paso raro, que encontraste raro, que detectaste",
    "Metaconocimiento: que tipo de informacion tienes → CAPABILITY_DISCOVERY",
    "Confidence score determinístico: exact=1.0, synonym=0.94, spelling=0.90, partial=0.78",
    "Timings NLP: spell_correction_ms, synonym_resolution_ms, intent_normalization_ms",
]


@dataclass(frozen=True)
class NlpTestCase:
    category: str
    question: str
    expected_intent: str
    rationale: str = ""


@dataclass
class NlpTestResult:
    case: NlpTestCase
    normalized_question: str
    corrections_applied: list[str]
    detected_intent: str
    intent_confidence: float
    match_type: str
    passed: bool
    elapsed_ms: float


@dataclass
class CategorySummary:
    category: str
    total: int = 0
    passed: int = 0

    @property
    def success_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100


TEST_SUITE: list[NlpTestCase] = [
    # --- Ortografía ---
    NlpTestCase("ortografia", "Que informasion tienes", Intent.CAPABILITY_DISCOVERY.value),
    NlpTestCase("ortografia", "Que infomacion tienes", Intent.CAPABILITY_DISCOVERY.value),
    NlpTestCase("ortografia", "Ke informacion tienes", Intent.CAPABILITY_DISCOVERY.value),
    NlpTestCase("ortografia", "Q informacion tienes", Intent.CAPABILITY_DISCOVERY.value),
    NlpTestCase("ortografia", "Que datos tienes", Intent.CAPABILITY_DISCOVERY.value),
    NlpTestCase("ortografia", "Que datos tines", Intent.CAPABILITY_DISCOVERY.value),
    NlpTestCase("ortografia", "Quien es el clinte mas fuerte", Intent.TOP_CLIENTES.value),
    NlpTestCase("ortografia", "Quien es el mejor clente", Intent.TOP_CLIENTES.value),
    NlpTestCase("ortografia", "Que paso en juno", Intent.MONTH_ANALYSIS.value),
    NlpTestCase("ortografia", "Que paso en diciemre", Intent.MONTH_ANALYSIS.value),
    # --- Sinónimos ---
    NlpTestCase("sinonimos", "Cliente principal", Intent.TOP_CLIENTES.value),
    NlpTestCase("sinonimos", "Cliente dominante", Intent.TOP_CLIENTES.value),
    NlpTestCase("sinonimos", "Cliente mas importante", Intent.TOP_CLIENTES.value),
    NlpTestCase("sinonimos", "Cliente mas fuerte", Intent.TOP_CLIENTES.value),
    NlpTestCase("sinonimos", "Quien compra mas", Intent.TOP_CLIENTES.value),
    NlpTestCase("sinonimos", "Proveedor principal", Intent.TOP_PROVEEDORES.value),
    NlpTestCase("sinonimos", "Proveedor dominante", Intent.TOP_PROVEEDORES.value),
    NlpTestCase("sinonimos", "Proveedor mas importante", Intent.TOP_PROVEEDORES.value),
    # --- Metaconocimiento ---
    NlpTestCase("metaconocimiento", "Que sabes", Intent.CAPABILITY_DISCOVERY.value),
    NlpTestCase("metaconocimiento", "Que conoces", Intent.CAPABILITY_DISCOVERY.value),
    NlpTestCase("metaconocimiento", "Que informacion tienes", Intent.CAPABILITY_DISCOVERY.value),
    NlpTestCase("metaconocimiento", "Que tipo de informacion tienes", Intent.CAPABILITY_DISCOVERY.value),
    NlpTestCase("metaconocimiento", "Que datos tienes", Intent.CAPABILITY_DISCOVERY.value),
    NlpTestCase("metaconocimiento", "Que puedes responder", Intent.CAPABILITY_DISCOVERY.value),
    NlpTestCase("metaconocimiento", "Que puedes hacer", Intent.CAPABILITY_DISCOVERY.value),
    # --- Cobertura ---
    NlpTestCase("cobertura", "Hasta cuando tienes datos", Intent.DATA_COVERAGE.value),
    NlpTestCase("cobertura", "Que periodo cubres", Intent.DATA_COVERAGE.value),
    NlpTestCase("cobertura", "De que fecha a que fecha sabes", Intent.DATA_COVERAGE.value),
    NlpTestCase("cobertura", "Hasta que fecha estas actualizado", Intent.DATA_COVERAGE.value),
    NlpTestCase("cobertura", "Que años tienes", Intent.DATA_COVERAGE.value),
    # --- Lenguaje coloquial ---
    NlpTestCase("coloquial", "Quien compra mas", Intent.TOP_CLIENTES.value),
    NlpTestCase("coloquial", "Quien vende mas", Intent.TOP_PROVEEDORES.value),
    NlpTestCase("coloquial", "Donde esta el negocio", Intent.BUSINESS_CONCENTRATION.value),
    NlpTestCase("coloquial", "Que paso raro este año", Intent.EXECUTIVE_INSIGHTS.value),
    NlpTestCase("coloquial", "Que hallazgos encontraste", Intent.EXECUTIVE_INSIGHTS.value),
    NlpTestCase("coloquial", "Quien mueve mas dinero", Intent.BUSINESS_CONCENTRATION.value),
    # --- Ambigüedad (éxito = UNKNOWN) ---
    NlpTestCase("ambiguedad", "Que onda", Intent.UNKNOWN.value),
    NlpTestCase("ambiguedad", "Hola", Intent.UNKNOWN.value),
    NlpTestCase("ambiguedad", "Ayudame", Intent.UNKNOWN.value),
    NlpTestCase("ambiguedad", "No entiendo", Intent.UNKNOWN.value),
    NlpTestCase("ambiguedad", "Que me recomiendas", Intent.UNKNOWN.value),
    NlpTestCase("ambiguedad", "Dime algo interesante", Intent.UNKNOWN.value),
]


def run_suite(hll: HumanLanguageLayer, router: IntentRouter) -> list[NlpTestResult]:
    results: list[NlpTestResult] = []
    for case in TEST_SUITE:
        started = time.perf_counter()
        hl = hll.process(case.question)
        match = router.route(
            hl.normalized_question,
            corrections_applied=hl.corrections_applied,
            intent_hint=hl.intent_hint,
        )
        elapsed_ms = (time.perf_counter() - started) * 1000
        passed = match.intent.value == case.expected_intent
        results.append(
            NlpTestResult(
                case=case,
                normalized_question=hl.normalized_question,
                corrections_applied=list(hl.corrections_applied),
                detected_intent=match.intent.value,
                intent_confidence=match.confidence,
                match_type=match.match_type,
                passed=passed,
                elapsed_ms=elapsed_ms,
            )
        )
    return results


def summarize_by_category(results: list[NlpTestResult]) -> dict[str, CategorySummary]:
    summaries: dict[str, CategorySummary] = {}
    for result in results:
        cat = result.case.category
        if cat not in summaries:
            summaries[cat] = CategorySummary(category=cat)
        summaries[cat].total += 1
        summaries[cat].passed += int(result.passed)
    return summaries


def print_results(results: list[NlpTestResult]) -> None:
    current_category = ""
    for result in results:
        if result.case.category != current_category:
            current_category = result.case.category
            print(f"\n{'=' * 72}")
            print(f"CATEGORIA: {current_category.upper()}")
            print("=" * 72)

        status = "PASS" if result.passed else "FAIL"
        print(f"\n[{status}] {result.case.question}")
        print(f"  Pregunta normalizada : {result.normalized_question}")
        print(f"  Correcciones         : {result.corrections_applied or '(ninguna)'}")
        print(f"  Intencion detectada  : {result.detected_intent}")
        print(f"  Confianza            : {result.intent_confidence:.2f} ({result.match_type})")
        print(f"  Intencion esperada   : {result.case.expected_intent}")
        print(f"  Tiempo total         : {result.elapsed_ms:.2f} ms")


def build_report(results: list[NlpTestResult], min_success: float) -> str:
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    success_pct = (passed / total * 100) if total else 0.0
    category_summaries = summarize_by_category(results)
    failures = [r for r in results if not r.passed]
    avg_ms = sum(r.elapsed_ms for r in results) / total if total else 0.0
    max_ms = max((r.elapsed_ms for r in results), default=0.0)
    delta = success_pct - BASELINE_SUCCESS

    meets_min = success_pct >= min_success
    meets_ideal = success_pct >= IDEAL_SUCCESS

    lines: list[str] = [
        "# Reporte de robustez NLP",
        "",
        "Validación determinística de Human Language Layer + Intent Router.",
        "Sin LLM, embeddings ni Ollama para clasificación.",
        "",
        "## Comparativa antes / después",
        "",
        "| Métrica | Antes | Después | Delta |",
        "|---------|-------|---------|-------|",
        f"| Porcentaje de éxito | {BASELINE_SUCCESS:.1f}% | **{success_pct:.1f}%** | +{delta:.1f} pp |",
        f"| Pruebas exitosas | 27/42 | {passed}/{total} | +{passed - 27} |",
        f"| Pruebas fallidas | 15 | {failed} | {failed - 15:+d} |",
        "",
        "## Resumen ejecutivo",
        "",
        "| Métrica | Valor |",
        "|---------|-------|",
        f"| Total pruebas | {total} |",
        f"| Pruebas exitosas | {passed} |",
        f"| Pruebas fallidas | {failed} |",
        f"| **Porcentaje de éxito** | **{success_pct:.1f}%** |",
        f"| Objetivo mínimo | {min_success:.0f}% |",
        f"| Objetivo ideal | {IDEAL_SUCCESS:.0f}% |",
        f"| Cumple mínimo | {'Si' if meets_min else 'No'} |",
        f"| Cumple ideal | {'Si' if meets_ideal else 'No'} |",
        f"| Tiempo promedio | {avg_ms:.2f} ms |",
        f"| Tiempo máximo | {max_ms:.2f} ms |",
        "",
        "## Resultados por categoría",
        "",
        "| Categoría | Total | Exitosas | Fallidas | Éxito |",
        "|-----------|-------|----------|----------|-------|",
    ]

    category_order = [
        "ortografia", "sinonimos", "metaconocimiento",
        "cobertura", "coloquial", "ambiguedad",
    ]
    for cat in category_order:
        summary = category_summaries.get(cat)
        if summary is None:
            continue
        failed_cat = summary.total - summary.passed
        lines.append(
            f"| {cat.capitalize()} | {summary.total} | {summary.passed} | "
            f"{failed_cat} | {summary.success_rate:.1f}% |"
        )

    lines.extend([
        "",
        "## Patrones añadidos en esta iteración",
        "",
    ])
    for pattern in PATTERNS_ADDED:
        lines.append(f"- {pattern}")

    lines.extend([
        "",
        "## Errores detectados",
        "",
    ])

    if failures:
        lines.append("| Pregunta | Esperada | Detectada | Confianza | Categoría |")
        lines.append("|----------|----------|-----------|-----------|-----------|")
        for result in failures:
            lines.append(
                f"| {result.case.question} | {result.case.expected_intent} | "
                f"{result.detected_intent} | {result.intent_confidence:.2f} | "
                f"{result.case.category} |"
            )
    else:
        lines.append("_Sin errores — todas las pruebas pasaron._")

    lines.extend([
        "",
        "## Casos aún no cubiertos / recomendaciones futuras",
        "",
    ])

    if failures:
        for result in failures:
            lines.append(
                f"- `{result.case.question}`: esperaba {result.case.expected_intent}, "
                f"detectó {result.detected_intent}"
            )
    else:
        lines.extend([
            "- Consultas con códigos de entidad en lenguaje coloquial (ej. \"cliente C0003\")",
            "- Preguntas mixtas de dos intenciones (ej. \"top clientes y KPIs del mes\")",
            "- Variantes regionales adicionales (ej. \"chamba\", \"fregado\")",
            "- Preguntas con números escritos en palabras (\"cliente número tres\")",
        ])

    lines.extend([
        "",
        "## Recomendación MVP",
        "",
    ])

    if success_pct >= IDEAL_SUCCESS:
        lines.append(
            f"Con **{success_pct:.1f}%** de éxito, el NLP determinístico supera el objetivo "
            f"ideal ({IDEAL_SUCCESS:.0f}%). **Recomendación: congelar la capa NLP del MVP** "
            "y registrar nuevas variantes vía diccionario extensible (`register_word`, "
            "`register_phrase`, `SynonymRule`) conforme aparezcan en producción."
        )
    elif success_pct >= min_success:
        lines.append(
            f"Con **{success_pct:.1f}%** de éxito se cumple el mínimo ({min_success:.0f}%) "
            f"pero no el ideal ({IDEAL_SUCCESS:.0f}%). **Recomendación: usable en MVP** "
            "con monitoreo de consultas UNKNOWN en observabilidad."
        )
    else:
        lines.append(
            f"Con **{success_pct:.1f}%** de éxito no se alcanza el mínimo. "
            "Se requiere otra iteración antes de congelar."
        )

    lines.extend([
        "",
        "## Detalle de pruebas",
        "",
    ])

    for cat in category_order:
        cat_results = [r for r in results if r.case.category == cat]
        if not cat_results:
            continue
        lines.append(f"### {cat.capitalize()}")
        lines.append("")
        for result in cat_results:
            status = "PASS" if result.passed else "FAIL"
            corrections = ", ".join(result.corrections_applied) or "ninguna"
            lines.append(f"- **[{status}]** `{result.case.question}`")
            lines.append(f"  - Normalizada: `{result.normalized_question}`")
            lines.append(f"  - Correcciones: {corrections}")
            lines.append(
                f"  - Intención: {result.detected_intent} "
                f"(confianza {result.intent_confidence:.2f}, {result.match_type})"
            )
            lines.append(f"  - Esperada: {result.case.expected_intent}")
            lines.append(f"  - Tiempo: {result.elapsed_ms:.2f} ms")
        lines.append("")

    lines.extend([
        "## Criterio de éxito",
        "",
        f"- Baseline anterior: **{BASELINE_SUCCESS:.1f}%**",
        f"- Objetivo mínimo: **{min_success:.0f}%**",
        f"- Objetivo ideal: **{IDEAL_SUCCESS:.0f}%**",
        f"- Resultado actual: **{success_pct:.1f}%**",
        "",
        "Generado por `scripts/test_nlp_robustness.py`.",
    ])

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Batería de robustez NLP")
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="Escribe docs/nlp_robustness_report.md",
    )
    parser.add_argument(
        "--min-success",
        type=float,
        default=MIN_SUCCESS_DEFAULT,
        help=f"Porcentaje mínimo de éxito requerido (default: {MIN_SUCCESS_DEFAULT})",
    )
    args = parser.parse_args()

    hll = HumanLanguageLayer()
    router = IntentRouter()
    results = run_suite(hll, router)

    print("\n" + "=" * 72)
    print("BATERIA DE ROBUSTEZ NLP — Human Language Layer")
    print("=" * 72)

    print_results(results)

    total = len(results)
    passed = sum(1 for r in results if r.passed)
    success_pct = (passed / total * 100) if total else 0.0

    print("\n" + "=" * 72)
    print("RESUMEN GLOBAL")
    print("=" * 72)
    print(f"Total pruebas    : {total}")
    print(f"Exitosas         : {passed}")
    print(f"Fallidas         : {total - passed}")
    print(f"Porcentaje exito : {success_pct:.1f}%")
    print(f"Baseline anterior: {BASELINE_SUCCESS:.1f}%")
    print(f"Delta            : +{success_pct - BASELINE_SUCCESS:.1f} pp")
    print(f"Objetivo minimo  : {args.min_success:.0f}% {'OK' if success_pct >= args.min_success else 'FAIL'}")
    print(f"Objetivo ideal   : {IDEAL_SUCCESS:.0f}% {'OK' if success_pct >= IDEAL_SUCCESS else 'FAIL'}")

    report = build_report(results, args.min_success)

    if args.write_report:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(report, encoding="utf-8")
        print(f"\nReporte escrito en: {REPORT_PATH}")

    if success_pct < args.min_success:
        sys.exit(1)


if __name__ == "__main__":
    main()
