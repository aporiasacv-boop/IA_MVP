from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from app.enterprise_knowledge.schemas import (
    EnterpriseKnowledgeObjectSchema,
    KnowledgeIdentity,
    KnowledgeItem,
    KnowledgeQuality,
)
from app.enterprise_reasoning.schemas import EnterpriseReasoningObjectSchema, ReasoningConfidence, ReasoningConclusion
from app.evidence_package.evidence_builder import build_evidence_package, package_size_bytes
from app.evidence_package.example_data import build_example_package
from app.semantic_intent.execution_planner import build_execution_plan
from app.semantic_intent.semantic_parser import parse_semantic_question


def _minimal_eko():
    now = datetime(2026, 6, 24)
    return EnterpriseKnowledgeObjectSchema(
        schema_version="1.0.0",
        canonical_id=1,
        identity=KnowledgeIdentity(
            canonical_id=1,
            canonical_name="TEST",
            normalized_name="TEST",
            alias_count=1,
            items=[
                KnowledgeItem(
                    key="canonical_name",
                    value="TEST",
                    source="canonical_business_entity",
                    evidence={},
                    confidence=Decimal("1.0"),
                    computed_at=now,
                )
            ],
        ),
        facts=[
            KnowledgeItem(
                key="total_movements",
                value=50,
                source="business_entity_profile",
                evidence={},
                confidence=Decimal("0.8"),
                computed_at=now,
            )
        ],
        quality=KnowledgeQuality(
            completeness=Decimal("0.8"),
            average_confidence=Decimal("0.8"),
            has_profile=True,
            has_ontology=True,
            ontology_assignment_count=1,
        ),
        evidence=[{"rule_code": "test"}],
    )


def test_build_package_from_plan() -> None:
    parse = parse_semantic_question("Listar clientes principales")
    plan = build_execution_plan(parse)
    eko = _minimal_eko()
    pkg = build_evidence_package(
        question=parse.original_question,
        plan=plan,
        eko=eko,
        ero=None,
        canonical_id=1,
    )
    assert pkg.question == parse.original_question
    assert len(pkg.knowledge) > 0
    assert pkg.metadata["contains_sql"] is False
    assert pkg.metadata["contains_llm_output"] is False


def test_build_package_missing_ero_limitation() -> None:
    parse = parse_semantic_question("Recomendar acciones para clientes")
    plan = build_execution_plan(parse)
    pkg = build_evidence_package(
        question=parse.original_question,
        plan=plan,
        eko=_minimal_eko(),
        ero=None,
        canonical_id=1,
    )
    codes = {lim.code for lim in pkg.limitations}
    assert "missing_ero" in codes


def test_example_package() -> None:
    pkg = build_example_package()
    assert pkg.package_id
    assert package_size_bytes(pkg) > 0


def test_build_with_ero_sections() -> None:
    now = datetime(2026, 6, 24)
    parse = parse_semantic_question("Recomendar acciones")
    plan = build_execution_plan(parse)
    ero = EnterpriseReasoningObjectSchema(
        schema_version="1.0.0",
        canonical_id=1,
        recommendations=[
            ReasoningConclusion(
                key="act",
                value={"action": "x"},
                rule_code="r1",
                evidence={},
                confidence=Decimal("0.8"),
                severity="medium",
                computed_at=now,
            )
        ],
        confidence=ReasoningConfidence(
            average_confidence=Decimal("0.8"),
            conclusions_count=1,
            rules_executed=5,
        ),
        evidence=[{"rule_code": "r1"}],
    )
    pkg = build_evidence_package(
        question=parse.original_question,
        plan=plan,
        eko=_minimal_eko(),
        ero=ero,
        canonical_id=1,
    )
    assert len(pkg.recommendations) == 1


def test_package_confidence_range() -> None:
    pkg = build_example_package()
    conf = float(pkg.confidence.average_confidence)
    assert 0 <= conf <= 1
