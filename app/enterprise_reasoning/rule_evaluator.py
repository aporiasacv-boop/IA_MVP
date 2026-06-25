from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from app.enterprise_knowledge.schemas import EnterpriseKnowledgeObjectSchema, KnowledgeItem
from app.enterprise_reasoning.schemas import ReasoningRuleDefinition


@dataclass
class EkoEvaluationContext:
    eko: EnterpriseKnowledgeObjectSchema
    facts: dict[str, Any] = field(default_factory=dict)
    alert_keys: set[str] = field(default_factory=set)
    signal_keys: set[str] = field(default_factory=set)
    role_codes: set[str] = field(default_factory=set)
    nature_codes: set[str] = field(default_factory=set)

    @classmethod
    def from_eko(cls, eko: EnterpriseKnowledgeObjectSchema) -> "EkoEvaluationContext":
        facts: dict[str, Any] = {}
        for item in eko.facts:
            facts[item.key] = item.value
        return cls(
            eko=eko,
            facts=facts,
            alert_keys={item.key for item in eko.alerts},
            signal_keys={item.key for item in eko.signals},
            role_codes={item.key for item in eko.roles},
            nature_codes={item.key for item in eko.nature},
        )

    def item_by_key(self, section: str, key: str) -> KnowledgeItem | None:
        items = getattr(self.eko, section, [])
        for item in items:
            if item.key == key:
                return item
        return None


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def evaluate_condition(ctx: EkoEvaluationContext, condition: dict) -> tuple[bool, dict]:
    if "all_of" in condition:
        evidence: dict = {"operator": "all_of", "matched": []}
        for sub in condition["all_of"]:
            ok, sub_evidence = evaluate_condition(ctx, sub)
            if not ok:
                return False, evidence
            evidence["matched"].append(sub_evidence)
        return True, evidence

    if "any_of" in condition:
        evidence = {"operator": "any_of", "matched": []}
        for sub in condition["any_of"]:
            ok, sub_evidence = evaluate_condition(ctx, sub)
            if ok:
                evidence["matched"].append(sub_evidence)
                return True, evidence
        return False, evidence

    if "not" in condition:
        ok, sub_evidence = evaluate_condition(ctx, condition["not"])
        return not ok, {"operator": "not", "inner": sub_evidence}

    if "eko_alert_present" in condition:
        key = condition["eko_alert_present"]
        matched = key in ctx.alert_keys
        item = ctx.item_by_key("alerts", key) if matched else None
        return matched, {"alert_key": key, "eko_evidence": item.evidence if item else {}}

    if "eko_signal_present" in condition:
        key = condition["eko_signal_present"]
        matched = key in ctx.signal_keys
        item = ctx.item_by_key("signals", key) if matched else None
        return matched, {"signal_key": key, "eko_evidence": item.evidence if item else {}}

    if "eko_alert_any" in condition:
        keys = set(condition["eko_alert_any"])
        matched = keys & ctx.alert_keys
        return bool(matched), {"matched_alerts": sorted(matched)}

    if "eko_signal_any" in condition:
        keys = set(condition["eko_signal_any"])
        matched = keys & ctx.signal_keys
        return bool(matched), {"matched_signals": sorted(matched)}

    if "eko_fact_min" in condition:
        spec = condition["eko_fact_min"]
        field_name = spec["field"]
        threshold = float(spec["threshold"])
        value = _to_float(ctx.facts.get(field_name))
        matched = value is not None and value >= threshold
        return matched, {"field": field_name, "value": value, "threshold": threshold}

    if "eko_fact_max" in condition:
        spec = condition["eko_fact_max"]
        field_name = spec["field"]
        threshold = float(spec["threshold"])
        value = _to_float(ctx.facts.get(field_name))
        matched = value is not None and value <= threshold
        return matched, {"field": field_name, "value": value, "threshold": threshold}

    if "eko_fact_equals" in condition:
        spec = condition["eko_fact_equals"]
        field_name = spec["field"]
        expected = spec["value"]
        actual = ctx.facts.get(field_name)
        matched = actual == expected
        return matched, {"field": field_name, "expected": expected, "actual": actual}

    if "eko_quality_min_completeness" in condition:
        threshold = float(condition["eko_quality_min_completeness"])
        value = float(ctx.eko.quality.completeness)
        return value >= threshold, {"completeness": value, "threshold": threshold}

    if "eko_quality_has_profile" in condition:
        expected = bool(condition["eko_quality_has_profile"])
        actual = ctx.eko.quality.has_profile
        return actual == expected, {"has_profile": actual}

    if "eko_quality_has_ontology" in condition:
        expected = bool(condition["eko_quality_has_ontology"])
        actual = ctx.eko.quality.has_ontology
        return actual == expected, {"has_ontology": actual}

    if "eko_roles_include" in condition:
        code = condition["eko_roles_include"]
        matched = code in ctx.role_codes
        item = ctx.item_by_key("roles", code) if matched else None
        return matched, {"role_code": code, "eko_evidence": item.evidence if item else {}}

    if "eko_nature_include" in condition:
        code = condition["eko_nature_include"]
        matched = code in ctx.nature_codes
        item = ctx.item_by_key("nature", code) if matched else None
        return matched, {"nature_code": code, "eko_evidence": item.evidence if item else {}}

    if "eko_roles_count_min" in condition:
        minimum = int(condition["eko_roles_count_min"])
        count = len(ctx.role_codes)
        return count >= minimum, {"roles_count": count, "minimum": minimum}

    if "eko_relationships_min" in condition:
        minimum = int(condition["eko_relationships_min"])
        count = len(ctx.eko.relationships)
        return count >= minimum, {"relationships_count": count, "minimum": minimum}

    return False, {"error": "unknown_condition", "condition": condition}


def resolve_conclusion_value(
    ctx: EkoEvaluationContext,
    rule: ReasoningRuleDefinition,
    match_evidence: dict,
) -> Any:
    if rule.value_from == "static":
        return rule.value
    if rule.value_from == "eko_alert" and rule.value_ref:
        item = ctx.item_by_key("alerts", rule.value_ref)
        return item.value if item else rule.value
    if rule.value_from == "eko_signal" and rule.value_ref:
        item = ctx.item_by_key("signals", rule.value_ref)
        return item.value if item else rule.value
    if rule.value_from == "eko_fact" and rule.value_ref:
        return ctx.facts.get(rule.value_ref, rule.value)
    if rule.value_from == "eko_role" and rule.value_ref:
        item = ctx.item_by_key("roles", rule.value_ref)
        return item.value if item else rule.value
    if rule.value_from == "match_evidence":
        return match_evidence
    return rule.value


def evaluate_rule(
    ctx: EkoEvaluationContext,
    rule: ReasoningRuleDefinition,
) -> tuple[bool, dict, Any]:
    matched, evidence = evaluate_condition(ctx, rule.conditions)
    if not matched:
        return False, evidence, None
    value = resolve_conclusion_value(ctx, rule, evidence)
    evidence["rule_code"] = rule.rule_code
    evidence["pack_id"] = rule.pack_id
    return True, evidence, value
