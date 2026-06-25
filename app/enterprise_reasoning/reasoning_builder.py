from datetime import datetime
from decimal import Decimal

from app.enterprise_knowledge.schemas import EnterpriseKnowledgeObjectSchema
from app.enterprise_reasoning.constants import ERO_SCHEMA_ID, ERO_VERSION
from app.enterprise_reasoning.rule_evaluator import EkoEvaluationContext, evaluate_rule
from app.enterprise_reasoning.rule_loader import load_enabled_rules
from app.enterprise_reasoning.schemas import (
    EnterpriseReasoningObjectSchema,
    ReasoningConclusion,
    ReasoningConfidence,
    ReasoningRuleDefinition,
)


def _bucket_for_type(ero: EnterpriseReasoningObjectSchema, conclusion_type: str) -> list[ReasoningConclusion]:
    return {
        "finding": ero.findings,
        "signal": ero.signals,
        "alert": ero.alerts,
        "risk": ero.risks,
        "opportunity": ero.opportunities,
        "recommendation": ero.recommendations,
    }.get(conclusion_type, ero.findings)


def _avg_confidence(conclusions: list[ReasoningConclusion]) -> Decimal:
    if not conclusions:
        return Decimal("0.0000")
    total = sum(float(item.confidence) for item in conclusions)
    return Decimal(str(round(total / len(conclusions), 4)))


def _filter_incompatible(
    matched: list[tuple[ReasoningRuleDefinition, ReasoningConclusion]],
) -> list[tuple[ReasoningRuleDefinition, ReasoningConclusion]]:
    result: list[tuple[ReasoningRuleDefinition, ReasoningConclusion]] = []
    fired_rules: list[ReasoningRuleDefinition] = []
    for rule, conclusion in matched:
        blocked = any(
            rule.rule_code in fired.incompatible_with or fired.rule_code in rule.incompatible_with
            for fired in fired_rules
        )
        if blocked:
            continue
        result.append((rule, conclusion))
        fired_rules.append(rule)
    return result


def build_enterprise_reasoning_object(
    *,
    eko: EnterpriseKnowledgeObjectSchema,
    rules: list[ReasoningRuleDefinition] | None = None,
    computed_at: datetime,
) -> tuple[EnterpriseReasoningObjectSchema, int]:
    active_rules = rules if rules is not None else load_enabled_rules()
    ctx = EkoEvaluationContext.from_eko(eko)
    canonical_id = eko.canonical_id

    ero = EnterpriseReasoningObjectSchema(
        schema_version=ERO_VERSION,
        canonical_id=canonical_id,
        confidence=ReasoningConfidence(
            average_confidence=Decimal("0.0000"),
            conclusions_count=0,
            rules_executed=0,
        ),
    )

    matched_pairs: list[tuple[ReasoningRuleDefinition, ReasoningConclusion]] = []
    evidence_index: list[dict] = []
    rules_executed = 0

    for rule in active_rules:
        rules_executed += 1
        ok, evidence, value = evaluate_rule(ctx, rule)
        if not ok:
            continue
        conclusion = ReasoningConclusion(
            key=rule.key,
            value=value,
            rule_code=rule.rule_code,
            evidence=evidence,
            confidence=rule.confidence,
            severity=rule.severity,
            computed_at=computed_at,
        )
        matched_pairs.append((rule, conclusion))
        evidence_index.append(
            {
                "rule_code": rule.rule_code,
                "pack_id": rule.pack_id,
                "conclusion_type": rule.conclusion_type,
                "key": rule.key,
            }
        )

    for rule, conclusion in _filter_incompatible(matched_pairs):
        bucket = _bucket_for_type(ero, rule.conclusion_type)
        bucket.append(conclusion)

    all_conclusions = (
        ero.findings
        + ero.signals
        + ero.alerts
        + ero.risks
        + ero.opportunities
        + ero.recommendations
    )
    avg_conf = _avg_confidence(all_conclusions)

    ero.evidence = evidence_index
    ero.confidence = ReasoningConfidence(
        average_confidence=avg_conf,
        conclusions_count=len(all_conclusions),
        rules_executed=rules_executed,
        items=[
            ReasoningConclusion(
                key="ero_average_confidence",
                value=float(avg_conf),
                rule_code="aggregate_confidence",
                evidence={"conclusions": len(all_conclusions)},
                confidence=avg_conf,
                severity="low",
                computed_at=computed_at,
            )
        ],
    )
    ero.metadata = {
        "schema_id": ERO_SCHEMA_ID,
        "built_at": computed_at.isoformat(),
        "source_eko_schema": eko.metadata.get("schema_id"),
        "rules_evaluated": rules_executed,
        "deterministic": True,
        "contains_sql": False,
        "contains_llm_output": False,
    }
    return ero, rules_executed


def ero_to_payload(ero: EnterpriseReasoningObjectSchema) -> dict:
    return ero.model_dump(mode="json")
