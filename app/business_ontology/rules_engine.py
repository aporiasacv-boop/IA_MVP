from dataclasses import dataclass
from decimal import Decimal

from app.business_ontology.constants import (
    COMMERCIAL_DIMENSIONS,
    GL_DIMENSION,
    MIN_SUGGESTION_SCORE,
)


@dataclass(frozen=True)
class OntologyEntityContext:
    canonical_id: int
    canonical_name: str
    primary_rfc: str | None
    normalized_name: str
    alias_count: int
    total_movements: int
    total_amount: Decimal
    debit_amount: Decimal
    credit_amount: Decimal
    debit_credit_ratio: Decimal | None
    related_accounts_count: int
    related_counterparties_count: int
    active_months: int
    dimensions_used: list[str]
    top_accounts: list[dict]
    top_counterparties: list[dict]
    currencies: list[str]


@dataclass(frozen=True)
class OntologySuggestion:
    canonical_id: int
    concept_category: str
    type_code: str
    rule_code: str
    score: Decimal
    confidence: Decimal
    evidence: dict


def _dimensions_set(ctx: OntologyEntityContext) -> set[str]:
    return set(ctx.dimensions_used or [])


def _account_codes(ctx: OntologyEntityContext) -> list[str]:
    return [str(item.get("code", "")) for item in (ctx.top_accounts or [])]


def _account_names_upper(ctx: OntologyEntityContext) -> list[str]:
    return [str(item.get("name", "")).upper() for item in (ctx.top_accounts or [])]


def _keyword_match(ctx: OntologyEntityContext, keywords: set[str]) -> tuple[bool, list[str]]:
    hits: list[str] = []
    for name in _account_names_upper(ctx):
        for keyword in keywords:
            if keyword in name:
                hits.append(keyword)
    for code in _account_codes(ctx):
        for keyword in keywords:
            if keyword in code.upper():
                hits.append(keyword)
    return bool(hits), sorted(set(hits))


def _prefix_share(ctx: OntologyEntityContext, prefixes: tuple[str, ...] | list[str]) -> float:
    accounts = ctx.top_accounts or []
    if not accounts:
        return 0.0
    total_movements = sum(int(item.get("movements", 0)) for item in accounts)
    if total_movements <= 0:
        return 0.0
    matched = 0
    for item in accounts:
        code = str(item.get("code", ""))
        if any(code.startswith(prefix) for prefix in prefixes):
            matched += int(item.get("movements", 0))
    return matched / total_movements


def evaluate_rule(ctx: OntologyEntityContext, rule_code: str, conditions: dict, score_weight: Decimal) -> OntologySuggestion | None:
    dims = _dimensions_set(ctx)
    evidence: dict = {"rule_code": rule_code, "dimensions_used": sorted(dims)}

    if ctx.total_movements <= 0 and conditions.get("min_movements", 0) > 0:
        return None

    min_movements = conditions.get("min_movements", 0)
    if ctx.total_movements < min_movements:
        return None

    if "requires_any_dimension" in conditions:
        required = set(conditions["requires_any_dimension"])
        if not dims & required:
            return None
        evidence["matched_dimensions"] = sorted(dims & required)

    if "requires_all_dimensions" in conditions:
        required = set(conditions["requires_all_dimensions"])
        if not required.issubset(dims):
            return None
        evidence["matched_dimensions"] = sorted(required)

    if "requires_dimension" in conditions:
        dim = conditions["requires_dimension"]
        if dim not in dims:
            return None
        evidence["matched_dimension"] = dim

    if "requires_only_dimension" in conditions:
        only = conditions["requires_only_dimension"]
        if dims != {only}:
            return None
        evidence["only_dimension"] = only

    if conditions.get("excludes_commercial"):
        if dims & COMMERCIAL_DIMENSIONS:
            return None
        evidence["commercial_excluded"] = True

    if "account_keywords" in conditions:
        keywords = set(conditions["account_keywords"])
        matched, hits = _keyword_match(ctx, keywords)
        if not matched:
            return None
        evidence["account_keyword_hits"] = hits

    if "account_prefix" in conditions:
        prefix = conditions["account_prefix"]
        share = _prefix_share(ctx, (prefix,))
        min_share = float(conditions.get("min_share", 0.5))
        if share < min_share:
            return None
        evidence["account_prefix"] = prefix
        evidence["prefix_share"] = round(share, 4)

    if "account_prefix_any" in conditions:
        prefixes = conditions["account_prefix_any"]
        share = _prefix_share(ctx, prefixes)
        min_share = float(conditions.get("min_share", 0.3))
        if share < min_share:
            return None
        evidence["account_prefixes"] = prefixes
        evidence["prefix_share"] = round(share, 4)

    if "debit_ratio_min" in conditions:
        ratio = float(ctx.debit_credit_ratio or 0)
        if ratio < float(conditions["debit_ratio_min"]):
            return None
        evidence["debit_credit_ratio"] = ratio

    if "credit_ratio_min" in conditions:
        if ctx.debit_credit_ratio is None or ctx.debit_credit_ratio <= 0:
            return None
        inv = float(1 / ctx.debit_credit_ratio)
        if inv < float(conditions["credit_ratio_min"]):
            return None
        evidence["credit_dominance"] = round(inv, 4)

    if conditions.get("credit_exceeds_debit"):
        if ctx.credit_amount <= ctx.debit_amount:
            return None
        evidence["credit_amount"] = str(ctx.credit_amount)
        evidence["debit_amount"] = str(ctx.debit_amount)

    if conditions.get("debit_exceeds_credit"):
        if ctx.debit_amount <= ctx.credit_amount:
            return None
        evidence["debit_amount"] = str(ctx.debit_amount)
        evidence["credit_amount"] = str(ctx.credit_amount)

    if "max_counterparties" in conditions:
        if ctx.related_counterparties_count > int(conditions["max_counterparties"]):
            return None
        evidence["related_counterparties_count"] = ctx.related_counterparties_count

    if "min_active_months" in conditions:
        if ctx.active_months < int(conditions["min_active_months"]):
            return None
        evidence["active_months"] = ctx.active_months

    if conditions.get("balanced_debit_credit"):
        if ctx.debit_amount <= 0 or ctx.credit_amount <= 0:
            return None
        ratio = float(ctx.debit_credit_ratio or 0)
        if ratio < 0.7 or ratio > 1.4:
            return None
        evidence["balanced_ratio"] = ratio

    # Confidence from profile completeness proxy
    movement_factor = min(ctx.total_movements / 100, 1.0) if ctx.total_movements else 0.3
    account_factor = min(ctx.related_accounts_count / 5, 1.0) if ctx.related_accounts_count else 0.2
    confidence = Decimal(str(round(float(score_weight) * (0.6 + 0.25 * movement_factor + 0.15 * account_factor), 4)))
    score = score_weight

    if float(score) < MIN_SUGGESTION_SCORE:
        return None

    evidence["total_movements"] = ctx.total_movements
  # type_code filled by engine from rule target
    return OntologySuggestion(
        canonical_id=ctx.canonical_id,
        concept_category="",  # filled by engine
        type_code="",
        rule_code=rule_code,
        score=score,
        confidence=min(confidence, Decimal("1.0000")),
        evidence=evidence,
    )


def generate_ontology_suggestions(
    ctx: OntologyEntityContext,
    rules: list[tuple[str, str, str, dict, Decimal]],
) -> list[OntologySuggestion]:
    """rules: (rule_code, concept_category, type_code, conditions, score_weight)"""
    results: list[OntologySuggestion] = []
    for rule_code, concept_category, type_code, conditions, score_weight in rules:
        suggestion = evaluate_rule(ctx, rule_code, conditions, score_weight)
        if suggestion is None:
            continue
        results.append(
            OntologySuggestion(
                canonical_id=ctx.canonical_id,
                concept_category=concept_category,
                type_code=type_code,
                rule_code=rule_code,
                score=suggestion.score,
                confidence=suggestion.confidence,
                evidence=suggestion.evidence,
            )
        )
    return results
