from app.semantic_intent.catalog_loader import load_enabled_verbs, load_verbs
from app.semantic_intent.execution_planner import build_execution_plan
from app.semantic_intent.health import validate_semantic_health
from app.semantic_intent.metrics import SemanticIntentMetrics
from app.semantic_intent.schemas import (
    SemanticParseRequest,
    SemanticParseResult,
    SemanticPlanRequest,
    SemanticStatisticsResponse,
    VerbCatalogResponse,
    BusinessExecutionPlan,
)
from app.semantic_intent.semantic_parser import parse_semantic_question


class SemanticIntentService:
    def get_verbs(self) -> VerbCatalogResponse:
        verbs = load_verbs()
        enabled = load_enabled_verbs()
        return VerbCatalogResponse(
            version="1.0.0",
            verbs=verbs,
            total=len(verbs),
            enabled_count=len(enabled),
        )

    def parse(self, request: SemanticParseRequest) -> SemanticParseResult:
        result = parse_semantic_question(request.question)
        SemanticIntentMetrics.record_parse(
            verb_id=result.business_verb.verb_id if result.business_verb else None,
            confidence=float(result.confidence),
        )
        return result

    def plan(self, request: SemanticPlanRequest) -> BusinessExecutionPlan:
        parse = parse_semantic_question(request.question)
        SemanticIntentMetrics.record_parse(
            verb_id=parse.business_verb.verb_id if parse.business_verb else None,
            confidence=float(parse.confidence),
        )
        plan = build_execution_plan(parse)
        SemanticIntentMetrics.record_plan(
            plan_id=plan.plan_id,
            verb_id=plan.detected_verb,
            confidence=float(plan.confidence),
            incomplete=plan.incomplete,
            incompatible=plan.incompatible_strategy,
            ambiguous_objects=any(obj.ambiguous for obj in parse.business_objects),
        )
        return plan

    def get_statistics(self) -> SemanticStatisticsResponse:
        snap = SemanticIntentMetrics.snapshot()
        return SemanticStatisticsResponse(**snap)

    def validate_health(self) -> dict:
        return validate_semantic_health(SemanticIntentMetrics.health_issues())

    def get_health_issues(self) -> dict:
        return SemanticIntentMetrics.health_issues()
