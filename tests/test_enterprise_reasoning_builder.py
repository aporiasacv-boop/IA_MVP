from datetime import datetime
from decimal import Decimal

import pytest

from app.enterprise_knowledge.knowledge_builder import build_enterprise_knowledge_object
from app.enterprise_reasoning.reasoning_builder import build_enterprise_reasoning_object
from app.enterprise_reasoning.schemas import ReasoningRuleDefinition


def _sample_eko():
    return build_enterprise_knowledge_object(
        canonical={
            "canonical_id": 1,
            "canonical_name": "WALMART",
            "normalized_name": "WALMART",
            "primary_rfc": None,
            "alias_count": 1,
        },
        aliases=[],
        profile={
            "profile_id": 1,
            "total_movements": 150,
            "total_amount": Decimal("50000"),
            "debit_credit_ratio": Decimal("2.5"),
            "related_counterparties_count": 5,
            "profile_completeness": Decimal("0.85"),
            "top_accounts": [],
            "top_counterparties": [],
        },
        ontology_assignments=[
            {
                "assignment_id": 1,
                "concept_category": "role",
                "type_code": "CLIENTE",
                "type_label": "Cliente",
                "rule_code": "role_client",
                "evidence_json": {},
                "confidence": Decimal("0.9"),
                "status": "pending",
            }
        ],
        computed_at=datetime(2026, 6, 24),
    )


def test_build_ero_from_eko() -> None:
    eko = _sample_eko()
    ero, rules_executed = build_enterprise_reasoning_object(eko=eko, computed_at=datetime(2026, 6, 24))
    assert ero.canonical_id == 1
    assert rules_executed > 0
    assert ero.metadata["contains_llm_output"] is False
    assert len(ero.evidence) > 0


def test_custom_rule_fires() -> None:
    eko = _sample_eko()
    rule = ReasoningRuleDefinition(
        rule_code="test_rule",
        conclusion_type="finding",
        key="test_finding",
        value={"ok": True},
        conditions={"eko_roles_include": "CLIENTE"},
        severity="low",
        confidence=Decimal("0.99"),
        pack_id="test",
    )
    ero, _ = build_enterprise_reasoning_object(
        eko=eko, rules=[rule], computed_at=datetime(2026, 6, 24)
    )
    assert any(f.key == "test_finding" for f in ero.findings)


def test_incompatible_rules_filtered() -> None:
    eko = _sample_eko()
    rules = [
        ReasoningRuleDefinition(
            rule_code="rule_a",
            conclusion_type="recommendation",
            key="action_a",
            value={"action": "a"},
            conditions={"eko_roles_include": "CLIENTE"},
            incompatible_with=["rule_b"],
            pack_id="test",
        ),
        ReasoningRuleDefinition(
            rule_code="rule_b",
            conclusion_type="recommendation",
            key="action_b",
            value={"action": "b"},
            conditions={"eko_roles_include": "CLIENTE"},
            pack_id="test",
        ),
    ]
    ero, _ = build_enterprise_reasoning_object(
        eko=eko, rules=rules, computed_at=datetime(2026, 6, 24)
    )
    rule_codes = {r.rule_code for r in ero.recommendations}
    assert "rule_a" in rule_codes
    assert "rule_b" not in rule_codes
