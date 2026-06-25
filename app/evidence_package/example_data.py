from datetime import datetime
from decimal import Decimal

from app.evidence_package.constants import EXAMPLE_QUESTION
from app.evidence_package.evidence_builder import build_evidence_package
from app.enterprise_knowledge.schemas import (
    EnterpriseKnowledgeObjectSchema,
    KnowledgeIdentity,
    KnowledgeItem,
    KnowledgeQuality,
)
from app.enterprise_reasoning.schemas import (
    EnterpriseReasoningObjectSchema,
    ReasoningConfidence,
    ReasoningConclusion,
)
from app.semantic_intent.execution_planner import build_execution_plan
from app.semantic_intent.semantic_parser import parse_semantic_question


def build_example_package():
    now = datetime(2026, 6, 24, 12, 0, 0)
    parse = parse_semantic_question(EXAMPLE_QUESTION)
    plan = build_execution_plan(parse, now=now)

    eko = EnterpriseKnowledgeObjectSchema(
        schema_version="1.0.0",
        canonical_id=1,
        identity=KnowledgeIdentity(
            canonical_id=1,
            canonical_name="WALMART",
            normalized_name="WALMART",
            alias_count=2,
            items=[
                KnowledgeItem(
                    key="canonical_name",
                    value="WALMART",
                    source="canonical_business_entity",
                    evidence={"canonical_id": 1},
                    confidence=Decimal("1.0000"),
                    computed_at=now,
                )
            ],
        ),
        facts=[
            KnowledgeItem(
                key="total_movements",
                value=150,
                source="business_entity_profile",
                evidence={"profile_id": 1},
                confidence=Decimal("0.8500"),
                computed_at=now,
            )
        ],
        signals=[
            KnowledgeItem(
                key="high_transaction_volume",
                value=150,
                source="business_entity_profile",
                evidence={"threshold": 100},
                confidence=Decimal("0.8500"),
                computed_at=now,
            )
        ],
        alerts=[],
        quality=KnowledgeQuality(
            completeness=Decimal("0.8500"),
            average_confidence=Decimal("0.8200"),
            has_profile=True,
            has_ontology=True,
            ontology_assignment_count=2,
        ),
        evidence=[{"source": "business_ontology", "rule_code": "role_client", "assignment_id": 1}],
    )

    ero = EnterpriseReasoningObjectSchema(
        schema_version="1.0.0",
        canonical_id=1,
        risks=[
            ReasoningConclusion(
                key="data_gap_profile",
                value={"gap_type": "profile", "status": "ok"},
                rule_code="risk_missing_profile",
                evidence={"alert_key": "missing_profile"},
                confidence=Decimal("0.9500"),
                severity="low",
                computed_at=now,
            )
        ],
        recommendations=[
            ReasoningConclusion(
                key="prioritize_key_account",
                value={"action": "prioritize_account"},
                rule_code="recommendation_deepen_relationship",
                evidence={"signal": "high_transaction_volume"},
                confidence=Decimal("0.8300"),
                severity="medium",
                computed_at=now,
            )
        ],
        confidence=ReasoningConfidence(
            average_confidence=Decimal("0.8400"),
            conclusions_count=2,
            rules_executed=18,
        ),
        evidence=[{"rule_code": "opportunity_high_volume", "pack_id": "commercial_opportunity"}],
    )

    return build_evidence_package(
        question=EXAMPLE_QUESTION,
        plan=plan,
        eko=eko,
        ero=ero,
        canonical_id=1,
        built_at=now,
    )
