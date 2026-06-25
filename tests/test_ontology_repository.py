from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from app.business_ontology.metrics import BusinessOntologyMetrics
from app.business_ontology.repository import BusinessOntologyRepository


def _scalar_session(value):
    session = MagicMock(spec=Session)
    session.scalar.return_value = value
    return session


def test_count_types() -> None:
    repo = BusinessOntologyRepository(_scalar_session(35))
    assert repo.count_types() == 35


def test_upsert_assignment_inserts() -> None:
    session = MagicMock(spec=Session)
    session.scalar.return_value = None
    repo = BusinessOntologyRepository(session)
    inserted = repo.upsert_assignment(
        canonical_id=1,
        concept_category="role",
        type_id=10,
        rule_code="role_client_dimension",
        evidence_json={"dimensions_used": ["cuenta_cliente"]},
        score=Decimal("0.9200"),
        confidence=Decimal("0.8500"),
        now=datetime(2026, 6, 24),
    )
    assert inserted is True
    session.add.assert_called_once()


def test_seed_taxonomy_if_empty() -> None:
    session = MagicMock(spec=Session)
    session.scalar.return_value = 0
    repo = BusinessOntologyRepository(session)
    count = repo.seed_taxonomy_if_empty(now=datetime(2026, 6, 24))
    assert count == len(__import__("app.business_ontology.taxonomy", fromlist=["INITIAL_TAXONOMY"]).INITIAL_TAXONOMY)


def test_seed_taxonomy_skips_when_exists() -> None:
    repo = BusinessOntologyRepository(_scalar_session(10))
    assert repo.seed_taxonomy_if_empty(now=datetime(2026, 6, 24)) == 0


def test_list_assignments() -> None:
    session = MagicMock(spec=Session)
    session.execute.return_value.scalar_one.return_value = 1
    session.execute.return_value.mappings.return_value.all.return_value = [
        {
            "assignment_id": 1,
            "canonical_id": 10,
            "concept_category": "role",
            "type_id": 5,
            "type_code": "CLIENTE",
            "type_label": "Cliente",
            "rule_code": "role_client_dimension",
            "evidence_json": {},
            "score": Decimal("0.92"),
            "confidence": Decimal("0.85"),
            "status": "pending",
            "created_at": datetime(2026, 6, 24),
            "canonical_name": "WALMART",
        }
    ]
    repo = BusinessOntologyRepository(session)
    rows, total = repo.list_assignments()
    assert total == 1
    assert rows[0]["type_code"] == "CLIENTE"


def test_find_health_issues() -> None:
    session = MagicMock(spec=Session)
    session.execute.return_value.mappings.return_value.all.side_effect = [[], [], [], [], []]
    repo = BusinessOntologyRepository(session)
    issues = repo.find_health_issues()
    assert issues["contradictory_rules"] == []


def test_fetch_active_rules() -> None:
    session = MagicMock(spec=Session)
    session.execute.return_value.mappings.return_value.all.return_value = [
        {"rule_code": "role_client_dimension", "concept_category": "role", "type_code": "CLIENTE",
         "conditions_json": {}, "score_weight": Decimal("0.92"), "target_type_id": 1}
    ]
    repo = BusinessOntologyRepository(session)
    assert repo.fetch_active_rules()[0]["rule_code"] == "role_client_dimension"


def test_fetch_entity_contexts() -> None:
    session = MagicMock(spec=Session)
    session.execute.return_value.mappings.return_value.all.return_value = [{"canonical_id": 1}]
    repo = BusinessOntologyRepository(session)
    assert repo.fetch_entity_contexts()[0]["canonical_id"] == 1


def test_list_ontology_entities() -> None:
    session = MagicMock(spec=Session)
    session.execute.return_value.scalar_one.return_value = 2
    session.execute.return_value.fetchall.return_value = [(1,), (2,)]
    repo = BusinessOntologyRepository(session)
    ids, total = repo.list_ontology_entities()
    assert total == 2
    assert ids == [1, 2]


def test_list_types() -> None:
    session = MagicMock(spec=Session)
    session.scalars.return_value.all.return_value = []
    repo = BusinessOntologyRepository(session)
    assert repo.list_types(concept_category="role") == []


def test_get_type_code_map() -> None:
    row = MagicMock()
    row.concept_category = "role"
    row.type_code = "CLIENTE"
    row.type_id = 5
    session = MagicMock(spec=Session)
    session.scalars.return_value.all.return_value = [row]
    repo = BusinessOntologyRepository(session)
    assert repo.get_type_code_map()[("role", "CLIENTE")] == 5


def test_seed_rules_if_empty() -> None:
    session = MagicMock(spec=Session)
    session.scalar.return_value = 0
    row = MagicMock()
    row.concept_category = "role"
    row.type_code = "CLIENTE"
    row.type_id = 1
    session.scalars.return_value.all.return_value = [row]
    repo = BusinessOntologyRepository(session)
    # types exist from scalars but count_rules returns 0
    count = repo.seed_rules_if_empty(now=datetime(2026, 6, 24))
    assert count >= 0


def test_average_confidence_and_counts() -> None:
    session = MagicMock(spec=Session)
    session.scalar.side_effect = [0.75, 10, 5]
    session.execute.return_value.scalar_one.side_effect = [8, 3]
    repo = BusinessOntologyRepository(session)
    assert repo.average_confidence() == 0.75
    assert repo.count_entities_with_assignments() == 8
    assert repo.count_entities_without_suggestions() == 3
