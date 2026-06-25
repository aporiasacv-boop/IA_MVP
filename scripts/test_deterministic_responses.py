"""Pruebas del Deterministic Response Engine — respuestas empresariales sin LLM."""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database.database import SessionLocal
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.executive_summary_repository import ExecutiveSummaryRepository
from app.repositories.insights_repository import InsightsRepository
from app.repositories.metadata_repository import MetadataRepository
from app.schemas.response_mode import ResponseMode
from app.services.analytics_service import AnalyticsService
from app.services.deterministic_response_engine import DeterministicResponseEngine
from app.services.entity_extraction_layer import EntityExtractionLayer
from app.services.human_language_layer import HumanLanguageLayer
from app.services.insights_engine import InsightsEngine
from app.services.intent_router import IntentRouter
from app.services.metadata_service import MetadataService
from app.services.response_mode_resolver import ResponseModeResolver
from app.services.timing_collector import TimingCollector

TEST_CASES = [
    "¿Quién es nuestro mejor cliente?",
    "¿Cuál es nuestro peor cliente?",
    "¿Cuál fue el mejor mes?",
    "¿Cuál fue el peor mes?",
    "Resume junio.",
    "¿Qué cliente creció más?",
    "¿Qué proveedor creció más?",
]

GENERATIVE_SAMPLES = [
    "¿Cuáles son los riesgos del negocio?",
    "¿Qué oportunidades detectas?",
    "Dame un resumen ejecutivo completo.",
]


@dataclass
class TestResult:
    question: str
    intent: str
    response_mode: str
    deterministic_ms: float
    llm_ms: float
    answer_preview: str
    ok: bool


def run_case(
    question: str,
    hll: HumanLanguageLayer,
    entity_layer: EntityExtractionLayer,
    router: IntentRouter,
    mode_resolver: ResponseModeResolver,
    engine: DeterministicResponseEngine,
) -> TestResult:
    timings = TimingCollector()
    hl = hll.process(question, timings=timings)
    entities = entity_layer.extract(
        hl.normalized_question,
        alternate_text=hl.original_question,
        timings=timings,
    )
    match = router.route(
        hl.normalized_question,
        corrections_applied=hl.corrections_applied,
        intent_hint=hl.intent_hint,
    )
    mode = mode_resolver.resolve(match.intent)

    llm_ms = 0.0
    deterministic_ms = 0.0
    answer = ""

    if mode == ResponseMode.DETERMINISTIC:
        result = engine.generate(match, entities, timings=timings)
        answer = result.answer
        deterministic_ms = timings.deterministic_ms
    else:
        llm_ms = 1.0

    ok = mode == ResponseMode.DETERMINISTIC and llm_ms == 0 and bool(answer)
    preview = answer.replace("\n", " ")[:180]
    return TestResult(
        question=question,
        intent=match.intent.value,
        response_mode=mode.value,
        deterministic_ms=deterministic_ms,
        llm_ms=llm_ms,
        answer_preview=preview,
        ok=ok,
    )


def main() -> int:
    print("=" * 80)
    print("TEST DETERMINISTIC RESPONSE ENGINE - IA_MVP")
    print("=" * 80)

    hll = HumanLanguageLayer()
    entity_layer = EntityExtractionLayer()
    router = IntentRouter()
    mode_resolver = ResponseModeResolver()

    deterministic_results: list[TestResult] = []
    generative_modes = 0

    with SessionLocal() as session:
        engine = DeterministicResponseEngine(
            executive_summary_repository=ExecutiveSummaryRepository(session),
            analytics_service=AnalyticsService(AnalyticsRepository(session)),
            insights_engine=InsightsEngine(InsightsRepository(session)),
            metadata_service=MetadataService(MetadataRepository(session)),
            insights_repository=InsightsRepository(session),
        )

        print("\nCasos determinísticos obligatorios\n")
        for question in TEST_CASES:
            result = run_case(question, hll, entity_layer, router, mode_resolver, engine)
            deterministic_results.append(result)
            status = "OK" if result.ok else "FAIL"
            print(f"[{status}] {question}")
            print(f"       intent          : {result.intent}")
            print(f"       response_mode   : {result.response_mode}")
            print(f"       deterministic_ms: {result.deterministic_ms:.2f}")
            print(f"       llm_ms          : {result.llm_ms}")
            print(f"       respuesta       : {result.answer_preview}")
            print()

        print("Muestra de intenciones generativas\n")
        for question in GENERATIVE_SAMPLES:
            hl = hll.process(question)
            match = router.route(hl.normalized_question)
            mode = mode_resolver.resolve(match.intent)
            generative_modes += int(mode == ResponseMode.GENERATIVE)
            print(f"  {question!r} -> {match.intent.value} / {mode.value}")

    passed = sum(1 for result in deterministic_results if result.ok)
    total = len(TEST_CASES)
    avg_det_ms = (
        sum(result.deterministic_ms for result in deterministic_results) / total
        if total
        else 0.0
    )

    total_modes = total + len(GENERATIVE_SAMPLES)
    deterministic_count = passed
    generative_count = len(GENERATIVE_SAMPLES)
    llm_reduction_pct = (deterministic_count / total_modes) * 100 if total_modes else 0.0

    print("")
    print("=" * 80)
    print("Metricas")
    print("=" * 80)
    print(f"  Respuestas deterministicas (casos obligatorios): {passed}/{total}")
    print(f"  Respuestas generativas (muestra control):        {generative_count}/{len(GENERATIVE_SAMPLES)}")
    print(f"  Tiempo promedio deterministic_ms:                  {avg_det_ms:.2f} ms")
    print(
        f"  Reduccion potencial de llamadas LLM en muestra:  "
        f"{llm_reduction_pct:.1f}% ({deterministic_count}/{total_modes})"
    )
    print(f"  Resultado final:                                 {passed}/{total} OK")

    if passed != total:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
