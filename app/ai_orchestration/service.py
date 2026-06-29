from app.ai_orchestration.constants import (
    EXECUTIVE_RESPONSE_SCHEMA_ID,
    EXECUTIVE_RESPONSE_VERSION,
    EXECUTIVE_VERBS,
    SUPPORTED_PROVIDERS,
)
from app.ai_orchestration.executive_response_engine import ExecutiveResponseEngine
from app.ai_orchestration.health import validate_orchestration_health
from app.ai_orchestration.metrics import LLMOrchestrationMetrics
from app.ai_orchestration.providers.factory import create_llm_provider_with_fallback
from app.ai_orchestration.schemas import (
    AICostSummaryResponse,
    ExecutiveGenerateRequest,
    ExecutiveResponse,
    ExecutiveSchemaResponse,
    OrchestrationHealthResponse,
    OrchestrationStatisticsResponse,
    ProviderCostItem,
)
from app.evidence_package.schemas import EnterpriseEvidencePackage
from app.evidence_package.service import EvidencePackageService
from app.evidence_package.schemas import EvidenceBuildRequest
from app.semantic_intent.semantic_parser import parse_semantic_question
from app.utils.text_normalizer import normalize_for_matching

_EXECUTIVE_PHRASE_PATTERNS: tuple[str, ...] = (
    "como ves el negocio",
    "panorama ejecutivo",
    "panorama del negocio",
    "dame un panorama",
    "que riesgos",
    "que oportunidades",
    "riesgos observas",
    "oportunidades detectas",
    "comportamiento del negocio",
    "analiza el comportamiento del negocio",
)


def is_executive_reasoning_candidate(question: str) -> bool:
    parse = parse_semantic_question(question)
    if parse.business_verb is not None and parse.business_verb.verb_id in EXECUTIVE_VERBS:
        return True
    normalized = normalize_for_matching(question)
    return any(pattern in normalized for pattern in _EXECUTIVE_PHRASE_PATTERNS)


class AIOrchestrationService:
    def __init__(
        self,
        evidence_service: EvidencePackageService,
        engine: ExecutiveResponseEngine | None = None,
    ) -> None:
        self._evidence_service = evidence_service
        self._engine = engine or ExecutiveResponseEngine(create_llm_provider_with_fallback())

    def get_schema(self) -> ExecutiveSchemaResponse:
        return ExecutiveSchemaResponse(
            schema_id=EXECUTIVE_RESPONSE_SCHEMA_ID,
            schema_version=EXECUTIVE_RESPONSE_VERSION,
            response_fields=[
                "executive_summary",
                "detailed_analysis",
                "confidence",
                "citations",
                "limitations",
                "provider",
                "model",
                "tokens_input",
                "tokens_output",
                "estimated_cost",
                "response_time",
            ],
            supported_providers=sorted(SUPPORTED_PROVIDERS),
            description=(
                "Executive Response Engine v1 — respuestas ejecutivas basadas "
                "exclusivamente en Enterprise Evidence Package"
            ),
        )

    def generate(self, request: ExecutiveGenerateRequest) -> ExecutiveResponse:
        package = self._evidence_service.build(
            EvidenceBuildRequest(
                question=request.question,
                canonical_id=request.canonical_id,
            )
        )
        return self.generate_from_package(package)

    def generate_from_package(self, package: EnterpriseEvidencePackage) -> ExecutiveResponse:
        return self._engine.generate(package)

    def get_statistics(self) -> OrchestrationStatisticsResponse:
        return OrchestrationStatisticsResponse(**LLMOrchestrationMetrics.snapshot())

    def get_cost_summary(self) -> AICostSummaryResponse:
        snap = LLMOrchestrationMetrics.cost_snapshot()
        return AICostSummaryResponse(
            cost_by_provider=[ProviderCostItem(**item) for item in snap["cost_by_provider"]],
            provider_comparison=[ProviderCostItem(**item) for item in snap["provider_comparison"]],
            **{k: v for k, v in snap.items() if k not in {"cost_by_provider", "provider_comparison"}},
        )

    def validate_health(self) -> OrchestrationHealthResponse:
        provider = self._engine._provider
        provider_health = provider.health()
        issues = LLMOrchestrationMetrics.health_issues()
        try:
            validate_orchestration_health(issues)
            status = "healthy"
        except Exception:
            status = "unhealthy"
        flat_issues = [
            {"type": key, "count": len(value), "items": value[-5:]}
            for key, value in issues.items()
            if value
        ]
        return OrchestrationHealthResponse(
            status=status,
            provider=provider.provider_name(),
            provider_healthy=provider_health.get("status") == "healthy",
            issues=flat_issues,
        )

    def format_executive_answer(self, response: ExecutiveResponse) -> str:
        parts = [response.executive_summary]
        if response.detailed_analysis and response.detailed_analysis != response.executive_summary:
            parts.append(response.detailed_analysis)
        if response.limitations:
            parts.append("Limitaciones: " + "; ".join(response.limitations))
        return "\n\n".join(parts)
