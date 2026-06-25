from datetime import date, datetime
from decimal import Decimal

from app.enterprise_knowledge.constants import (
    EKO_SCHEMA_ID,
    EKO_VERSION,
    SOURCE_CANONICAL,
    SOURCE_MASTER,
    SOURCE_ONTOLOGY,
    SOURCE_PROFILE,
)
from app.enterprise_knowledge.schemas import (
    EnterpriseKnowledgeObjectSchema,
    KnowledgeIdentity,
    KnowledgeItem,
    KnowledgeQuality,
)


def _item(
    key: str,
    value,
    source: str,
    evidence: dict,
    confidence: Decimal,
    computed_at: datetime,
) -> KnowledgeItem:
    return KnowledgeItem(
        key=key,
        value=value,
        source=source,
        evidence=evidence,
        confidence=confidence,
        computed_at=computed_at,
    )


def _serialize_value(value) -> object:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_serialize_value(v) for v in value]
    return value


def _avg_confidence(items: list[KnowledgeItem]) -> Decimal:
    if not items:
        return Decimal("0.0000")
    total = sum(float(item.confidence) for item in items)
    return Decimal(str(round(total / len(items), 4)))


def build_enterprise_knowledge_object(
    *,
    canonical: dict,
    aliases: list[dict],
    profile: dict | None,
    ontology_assignments: list[dict],
    computed_at: datetime,
) -> EnterpriseKnowledgeObjectSchema:
    canonical_id = int(canonical["canonical_id"])
    evidence_index: list[dict] = []

    identity_items = [
        _item(
            "canonical_name",
            canonical["canonical_name"],
            SOURCE_CANONICAL,
            {"field": "canonical_name", "canonical_id": canonical_id},
            Decimal("1.0000"),
            computed_at,
        ),
        _item(
            "alias_count",
            int(canonical["alias_count"]),
            SOURCE_CANONICAL,
            {"alias_count": int(canonical["alias_count"])},
            Decimal("1.0000"),
            computed_at,
        ),
    ]

    for alias in aliases:
        identity_items.append(
            _item(
                f"alias:{alias['entity_code']}",
                {
                    "entity_code": alias["entity_code"],
                    "entity_name": alias["entity_name"],
                    "source_column": alias["source_column"],
                },
                SOURCE_MASTER,
                {
                    "entity_id": alias["entity_id"],
                    "resolution_rule": alias.get("resolution_rule"),
                    "resolution_score": str(alias.get("resolution_score", "")),
                },
                Decimal(str(alias.get("resolution_score", "1.0000"))),
                computed_at,
            )
        )

    identity = KnowledgeIdentity(
        canonical_id=canonical_id,
        canonical_name=canonical["canonical_name"],
        normalized_name=canonical["normalized_name"],
        primary_rfc=canonical.get("primary_rfc"),
        alias_count=int(canonical["alias_count"]),
        aliases=aliases,
        items=identity_items,
    )

    roles: list[KnowledgeItem] = []
    nature: list[KnowledgeItem] = []
    behaviors: list[KnowledgeItem] = []
    facts: list[KnowledgeItem] = []
    signals: list[KnowledgeItem] = []
    alerts: list[KnowledgeItem] = []
    patterns: list[KnowledgeItem] = []
    relationships: list[KnowledgeItem] = []

    for assignment in ontology_assignments:
        category = assignment["concept_category"]
        item = _item(
            assignment["type_code"],
            {
                "type_label": assignment["type_label"],
                "status": assignment["status"],
            },
            SOURCE_ONTOLOGY,
            {
                "rule_code": assignment["rule_code"],
                "evidence": assignment.get("evidence_json") or {},
                "assignment_id": assignment["assignment_id"],
            },
            Decimal(str(assignment["confidence"])),
            computed_at,
        )
        evidence_index.append(
            {
                "source": SOURCE_ONTOLOGY,
                "rule_code": assignment["rule_code"],
                "assignment_id": assignment["assignment_id"],
            }
        )
        if category == "role":
            roles.append(item)
        elif category == "nature":
            nature.append(item)
        elif category == "behavior":
            behaviors.append(item)
        elif category == "identity":
            identity_items.append(item)

    if profile:
        profile_confidence = Decimal(str(profile.get("profile_completeness", "0.8")))
        fact_fields = {
            "total_movements": profile.get("total_movements", 0),
            "total_amount": profile.get("total_amount"),
            "average_amount": profile.get("average_amount"),
            "debit_amount": profile.get("debit_amount"),
            "credit_amount": profile.get("credit_amount"),
            "debit_credit_ratio": profile.get("debit_credit_ratio"),
            "active_months": profile.get("active_months", 0),
            "active_days": profile.get("active_days", 0),
            "related_accounts_count": profile.get("related_accounts_count", 0),
            "related_counterparties_count": profile.get("related_counterparties_count", 0),
            "first_seen": profile.get("first_seen"),
            "last_seen": profile.get("last_seen"),
            "currencies": profile.get("currencies") or [],
            "dimensions_used": profile.get("dimensions_used") or [],
        }
        for key, value in fact_fields.items():
            if value is None or value == "" or value == []:
                continue
            facts.append(
                _item(
                    key,
                    _serialize_value(value),
                    SOURCE_PROFILE,
                    {"profile_id": profile.get("profile_id"), "field": key},
                    profile_confidence,
                    computed_at,
                )
            )

        monthly = profile.get("monthly_distribution") or {}
        if monthly:
            patterns.append(
                _item(
                    "monthly_activity",
                    _serialize_value(monthly),
                    SOURCE_PROFILE,
                    {"periods": len(monthly)},
                    profile_confidence,
                    computed_at,
                )
            )
            amounts = [float(v.get("amount", 0) if isinstance(v, dict) else 0) for v in monthly.values()]
            if amounts:
                peak = max(amounts)
                avg = sum(amounts) / len(amounts)
                if peak > avg * 2:
                    signals.append(
                        _item(
                            "seasonal_peak",
                            {"peak_amount": peak, "average_amount": round(avg, 4)},
                            SOURCE_PROFILE,
                            {"periods": len(monthly)},
                            Decimal("0.7500"),
                            computed_at,
                        )
                    )

        movements = int(profile.get("total_movements", 0))
        if movements >= 100:
            signals.append(
                _item(
                    "high_transaction_volume",
                    movements,
                    SOURCE_PROFILE,
                    {"threshold": 100},
                    Decimal("0.8500"),
                    computed_at,
                )
            )
        if movements == 0:
            alerts.append(
                _item(
                    "no_movements",
                    True,
                    SOURCE_PROFILE,
                    {"total_movements": 0},
                    Decimal("1.0000"),
                    computed_at,
                )
            )

        ratio = profile.get("debit_credit_ratio")
        if ratio is not None and float(ratio) > 2.0:
            signals.append(
                _item(
                    "debit_dominant",
                    float(ratio),
                    SOURCE_PROFILE,
                    {"debit_credit_ratio": float(ratio)},
                    Decimal("0.8000"),
                    computed_at,
                )
            )
        elif ratio is not None and float(ratio) < 0.5:
            signals.append(
                _item(
                    "credit_dominant",
                    float(ratio),
                    SOURCE_PROFILE,
                    {"debit_credit_ratio": float(ratio)},
                    Decimal("0.8000"),
                    computed_at,
                )
            )

        for account in profile.get("top_accounts") or []:
            relationships.append(
                _item(
                    f"account:{account.get('code')}",
                    _serialize_value(account),
                    SOURCE_PROFILE,
                    {"relation_type": "account"},
                    profile_confidence,
                    computed_at,
                )
            )
        for counterparty in profile.get("top_counterparties") or []:
            relationships.append(
                _item(
                    f"counterparty:{counterparty.get('code')}",
                    _serialize_value(counterparty),
                    SOURCE_PROFILE,
                    {"relation_type": "counterparty", "dimension": counterparty.get("dimension")},
                    profile_confidence,
                    computed_at,
                )
            )
    else:
        alerts.append(
            _item(
                "missing_profile",
                True,
                SOURCE_PROFILE,
                {"canonical_id": canonical_id},
                Decimal("1.0000"),
                computed_at,
            )
        )

    if not ontology_assignments:
        alerts.append(
            _item(
                "missing_ontology",
                True,
                SOURCE_ONTOLOGY,
                {"canonical_id": canonical_id},
                Decimal("1.0000"),
                computed_at,
            )
        )

    pending_roles = [a for a in ontology_assignments if a.get("concept_category") == "role"]
    if len({a["type_code"] for a in pending_roles}) > 2:
        alerts.append(
            _item(
                "ambiguous_roles",
                [a["type_code"] for a in pending_roles],
                SOURCE_ONTOLOGY,
                {"role_count": len(pending_roles)},
                Decimal("0.7000"),
                computed_at,
            )
        )

    pending_natures = [a for a in ontology_assignments if a.get("concept_category") == "nature"]
    if len({a["type_code"] for a in pending_natures if a.get("type_code") != "OTRO"}) > 1:
        alerts.append(
            _item(
                "conflicting_natures",
                [a["type_code"] for a in pending_natures],
                SOURCE_ONTOLOGY,
                {"nature_count": len(pending_natures)},
                Decimal("0.6500"),
                computed_at,
            )
        )

    all_items = identity_items + roles + nature + behaviors + facts + signals + patterns + relationships
    avg_conf = _avg_confidence(all_items)
    profile_completeness = Decimal(str(profile.get("profile_completeness", 0))) if profile else Decimal("0")
    section_scores = [
        1 if identity_items else 0,
        1 if roles or nature or behaviors else 0,
        1 if facts else 0,
        1 if signals or patterns else 0,
        1 if relationships else 0,
        1 if profile else 0,
        1 if ontology_assignments else 0,
    ]
    completeness = Decimal(str(round(sum(section_scores) / len(section_scores), 4)))

    quality = KnowledgeQuality(
        completeness=completeness,
        average_confidence=avg_conf,
        profile_completeness=profile_completeness if profile else None,
        has_profile=profile is not None,
        has_ontology=bool(ontology_assignments),
        ontology_assignment_count=len(ontology_assignments),
        items=[
            _item(
                "eko_completeness",
                float(completeness),
                "enterprise_knowledge",
                {"sections_filled": sum(section_scores), "sections_total": len(section_scores)},
                completeness,
                computed_at,
            )
        ],
    )

    return EnterpriseKnowledgeObjectSchema(
        schema_version=EKO_VERSION,
        canonical_id=canonical_id,
        identity=identity,
        roles=roles,
        nature=nature,
        behaviors=behaviors,
        facts=facts,
        signals=signals,
        alerts=alerts,
        patterns=patterns,
        relationships=relationships,
        quality=quality,
        evidence=evidence_index,
        metadata={
            "schema_id": EKO_SCHEMA_ID,
            "built_at": computed_at.isoformat(),
            "sources": [SOURCE_MASTER, SOURCE_CANONICAL, SOURCE_PROFILE, SOURCE_ONTOLOGY],
            "deterministic": True,
            "contains_sql": False,
            "contains_llm_output": False,
        },
    )


def eko_to_payload(eko: EnterpriseKnowledgeObjectSchema) -> dict:
    return eko.model_dump(mode="json")
