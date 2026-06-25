import hashlib
from datetime import datetime
from decimal import Decimal

from app.semantic_intent.catalog_loader import load_objects
from app.semantic_intent.constants import SBEP_SCHEMA_ID, SBEP_VERSION
from app.semantic_intent.schemas import BusinessExecutionPlan, SemanticParseResult

VERB_KNOWLEDGE_MAP: dict[str, list[str]] = {
    "informative": ["identity", "facts"],
    "analytic": ["identity", "facts", "patterns", "signals", "relationships"],
    "executive": ["identity", "facts", "signals", "alerts", "quality", "evidence"],
    "conversational": ["identity", "roles", "quality"],
    "future": [],
}

VERB_REASONING_MAP: dict[str, list[str]] = {
    "informative": [],
    "analytic": ["findings", "signals"],
    "executive": ["risks", "opportunities", "recommendations", "findings"],
    "conversational": ["findings"],
    "future": [],
}

VERB_STRATEGY_MAP: dict[str, str] = {
    "informative": "eko_identity_lookup",
    "analytic": "eko_full_analysis",
    "executive": "eko_ero_combined",
    "conversational": "ontology_exploration",
    "future": "unknown",
}

VERB_EVIDENCE_MAP: dict[str, list[str]] = {
    "informative": ["eko_identity"],
    "analytic": ["eko_facts", "eko_patterns"],
    "executive": ["eko_evidence", "ero_evidence", "ero_recommendations"],
    "conversational": ["eko_identity", "eko_roles"],
    "future": [],
}

EXECUTIVE_VERBS = {
    "evaluar", "diagnosticar", "justificar", "recomendar", "priorizar", "interpretar",
}
INFORMATIVE_VERBS = {"mostrar", "listar", "obtener", "consultar"}


def _unique_sorted(items: list[str]) -> list[str]:
    return sorted(set(items))


def _merge_object_requirements(object_ids: list[str]) -> tuple[list[str], list[str]]:
    eko: set[str] = set()
    ero: set[str] = set()
    obj_map = {obj.object_id: obj for obj in load_objects()}
    for object_id in object_ids:
        definition = obj_map.get(object_id)
        if definition is None:
            continue
        eko.update(definition.eko_sections)
        ero.update(definition.ero_sections)
    return sorted(eko), sorted(ero)


def _refine_strategy(verb_id: str | None, category: str | None, object_ids: list[str]) -> str:
    if verb_id in {"recomendar", "priorizar"}:
        return "ero_recommendation_review"
    if verb_id in {"diagnosticar", "evaluar"} or "riesgo" in object_ids:
        return "ero_risk_assessment"
    if verb_id in INFORMATIVE_VERBS and object_ids:
        return "eko_profile_summary"
    if verb_id in {"que_sabes", "como_funciona"}:
        return "capability_discovery"
    if category:
        return VERB_STRATEGY_MAP.get(category, "unknown")
    return "unknown"


def _is_incompatible(verb_id: str | None, category: str | None, strategy: str) -> bool:
    if verb_id in EXECUTIVE_VERBS and strategy == "eko_identity_lookup":
        return True
    if verb_id in INFORMATIVE_VERBS and strategy == "ero_recommendation_review":
        return True
    if category == "future":
        return True
    return False


def _is_incomplete(
    verb_id: str | None,
    required_knowledge: list[str],
    required_reasoning: list[str],
    strategy: str,
) -> bool:
    if strategy == "unknown":
        return True
    if verb_id is None:
        return True
    if not required_knowledge and strategy not in {"capability_discovery", "unknown"}:
        return True
    return False


def build_execution_plan(parse: SemanticParseResult, *, now: datetime | None = None) -> BusinessExecutionPlan:
    timestamp = now or datetime.now()
    verb = parse.business_verb
    verb_id = verb.verb_id if verb else None
    category = verb.category if verb else None
    object_ids = [obj.object_id for obj in parse.business_objects]

    required_knowledge = list(VERB_KNOWLEDGE_MAP.get(category or "", []))
    required_reasoning = list(VERB_REASONING_MAP.get(category or "", []))
    required_evidence = list(VERB_EVIDENCE_MAP.get(category or "", []))

    obj_eko, obj_ero = _merge_object_requirements(object_ids)
    required_knowledge = _unique_sorted(required_knowledge + obj_eko)
    required_reasoning = _unique_sorted(required_reasoning + obj_ero)

    if parse.business_constraints:
        if "alerts" not in required_knowledge:
            required_knowledge.append("alerts")
        if "risks" not in required_reasoning:
            required_reasoning.append("risks")

    if parse.entity_hints and "identity" not in required_knowledge:
        required_knowledge.insert(0, "identity")

    strategy = _refine_strategy(verb_id, category, object_ids)
    incompatible = _is_incompatible(verb_id, category, strategy)
    incomplete = _is_incomplete(verb_id, required_knowledge, required_reasoning, strategy)

    confidence = parse.confidence
    if incomplete:
        confidence = Decimal(str(round(float(confidence) * 0.7, 4)))
    if incompatible:
        confidence = Decimal(str(round(float(confidence) * 0.6, 4)))

    plan_id = hashlib.sha256(
        f"{parse.original_question}|{verb_id}|{','.join(object_ids)}|{strategy}".encode()
    ).hexdigest()[:16]

    return BusinessExecutionPlan(
        schema_version=SBEP_VERSION,
        plan_id=plan_id,
        original_question=parse.original_question,
        detected_verb=verb_id,
        detected_objects=object_ids,
        detected_context=parse.business_context,
        detected_timeframe=parse.business_time,
        required_knowledge=required_knowledge,
        required_reasoning=required_reasoning,
        required_evidence=required_evidence,
        execution_strategy=strategy,
        confidence=confidence,
        entity_hints=parse.entity_hints,
        constraints=parse.business_constraints,
        incomplete=incomplete,
        incompatible_strategy=incompatible,
        planned_at=timestamp,
        metadata={
            "schema_id": SBEP_SCHEMA_ID,
            "verb_category": category,
            "business_scope": parse.business_scope,
            "deterministic": True,
            "contains_sql": False,
            "contains_llm_output": False,
        },
    )
