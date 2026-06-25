import re
import time
from decimal import Decimal

from app.ai_orchestration.hallucination_guard import (
    INSUFFICIENT_EVIDENCE_ANALYSIS,
    INSUFFICIENT_EVIDENCE_SUMMARY,
    evaluate_evidence_sufficiency,
    validate_llm_response,
)
from app.ai_orchestration.metrics import LLMOrchestrationMetrics
from app.ai_orchestration.prompt_builder import build_executive_prompt, package_confidence_value
from app.ai_orchestration.providers.base import BaseLLMProvider
from app.ai_orchestration.schemas import EvidenceCitation, ExecutiveResponse
from app.evidence_package.schemas import EnterpriseEvidencePackage, EvidenceItem


_SUMMARY_PATTERN = re.compile(
    r"RESUMEN\s+EJECUTIVO\s*:?\s*(.*?)(?=ANÁLISIS\s+DETALLADO|ANALISIS\s+DETALLADO|$)",
    re.IGNORECASE | re.DOTALL,
)
_ANALYSIS_PATTERN = re.compile(
    r"AN[ÁA]LISIS\s+DETALLADO\s*:?\s*(.*)$",
    re.IGNORECASE | re.DOTALL,
)


def _parse_sections(text: str) -> tuple[str, str]:
    summary_match = _SUMMARY_PATTERN.search(text)
    analysis_match = _ANALYSIS_PATTERN.search(text)
    if summary_match and analysis_match:
        return summary_match.group(1).strip(), analysis_match.group(1).strip()
    if summary_match:
        return summary_match.group(1).strip(), text.strip()
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if len(paragraphs) >= 2:
        return paragraphs[0], "\n\n".join(paragraphs[1:])
    return text.strip(), text.strip()


def _extract_citations(package: EnterpriseEvidencePackage, text: str) -> list[EvidenceCitation]:
    citations: list[EvidenceCitation] = []
    lowered = text.lower()
    for item in package.knowledge + package.reasoning + package.facts + package.recommendations:
        if item.key.lower() in lowered or str(item.value).lower() in lowered:
            citations.append(
                EvidenceCitation(key=item.key, source=item.source, confidence=item.confidence)
            )
    return citations[:20]


def _limitations_text(package: EnterpriseEvidencePackage) -> list[str]:
    return [lim.description for lim in package.limitations]


class ExecutiveResponseEngine:
    """Motor ejecutivo que consume EXCLUSIVAMENTE Enterprise Evidence Package."""

    def __init__(self, provider: BaseLLMProvider) -> None:
        self._provider = provider

    def generate(self, package: EnterpriseEvidencePackage) -> ExecutiveResponse:
        started = time.perf_counter()
        guard = evaluate_evidence_sufficiency(package)
        limitations = _limitations_text(package)

        if guard.insufficient_evidence:
            LLMOrchestrationMetrics.record_request(
                provider=self._provider.provider_name(),
                model=self._provider.model_name,
                tokens_input=0,
                tokens_output=0,
                estimated_cost=0.0,
                response_time=time.perf_counter() - started,
                hallucination_guard=True,
                user_id=None,
            )
            return ExecutiveResponse(
                executive_summary=INSUFFICIENT_EVIDENCE_SUMMARY,
                detailed_analysis=INSUFFICIENT_EVIDENCE_ANALYSIS,
                confidence=Decimal("0.0000"),
                citations=[],
                limitations=limitations or [guard.reason or "Evidencia insuficiente"],
                provider=self._provider.provider_name(),
                model=self._provider.model_name,
                tokens_input=0,
                tokens_output=0,
                estimated_cost=0.0,
                response_time=round(time.perf_counter() - started, 4),
                hallucination_guard_triggered=True,
                evidence_package_id=package.package_id,
            )

        prompt = build_executive_prompt(package)
        llm_result = self._provider.generate_response(prompt)
        response_guard = validate_llm_response(llm_result.text, package)
        hallucination_triggered = response_guard.triggered

        executive_summary, detailed_analysis = _parse_sections(llm_result.text)
        if hallucination_triggered and guard.reason:
            limitations = limitations + [response_guard.reason or ""]

        citations = _extract_citations(package, llm_result.text)
        if not citations:
            citations = _extract_citations(package, executive_summary + detailed_analysis)

        pkg_confidence = package_confidence_value(package)
        if hallucination_triggered:
            confidence = Decimal("0.1000")
        else:
            confidence = pkg_confidence

        cost = self._provider.estimated_cost(
            llm_result.tokens_input,
            llm_result.tokens_output,
        )
        elapsed = round(time.perf_counter() - started, 4)

        LLMOrchestrationMetrics.record_request(
            provider=llm_result.provider or self._provider.provider_name(),
            model=llm_result.model or self._provider.model_name,
            tokens_input=llm_result.tokens_input,
            tokens_output=llm_result.tokens_output,
            estimated_cost=cost,
            response_time=elapsed,
            hallucination_guard=hallucination_triggered,
            user_id=None,
        )

        return ExecutiveResponse(
            executive_summary=executive_summary,
            detailed_analysis=detailed_analysis,
            confidence=confidence,
            citations=citations,
            limitations=limitations,
            provider=llm_result.provider or self._provider.provider_name(),
            model=llm_result.model or self._provider.model_name,
            tokens_input=llm_result.tokens_input,
            tokens_output=llm_result.tokens_output,
            estimated_cost=cost,
            response_time=elapsed,
            hallucination_guard_triggered=hallucination_triggered,
            evidence_package_id=package.package_id,
        )
