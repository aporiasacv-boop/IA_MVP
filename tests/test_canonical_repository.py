from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from app.canonical_business_entity.repository import CanonicalBusinessEntityRepository
from app.models.business_entity_master import BusinessEntityMaster
from app.models.canonical_business_entity import (
    CanonicalBusinessEntity,
    CanonicalEntitySuggestion,
)


def _scalar_session(return_value):
    session = MagicMock(spec=Session)
    session.scalar.return_value = return_value
    return session


def test_count_canonical_returns_zero_when_empty() -> None:
    repo = CanonicalBusinessEntityRepository(_scalar_session(0))
    assert repo.count_canonical() == 0


def test_count_commercial_entities() -> None:
    repo = CanonicalBusinessEntityRepository(_scalar_session(42))
    assert repo.count_commercial_entities() == 42


def test_count_resolved_commercial_reads_sql() -> None:
    session = MagicMock(spec=Session)
    session.execute.return_value.mappings.return_value.one.return_value = {"resolved": 30}
    repo = CanonicalBusinessEntityRepository(session)
    assert repo.count_resolved_commercial() == 30


def test_count_canonical_matches_reads_sql() -> None:
    session = MagicMock(spec=Session)
    session.execute.return_value.mappings.return_value.one.return_value = {"matched": 5}
    repo = CanonicalBusinessEntityRepository(session)
    assert repo.count_canonical_matches() == 5


def test_count_pending_and_automatic_suggestions() -> None:
    session = MagicMock(spec=Session)
    session.scalar.side_effect = [3, 10]
    repo = CanonicalBusinessEntityRepository(session)
    assert repo.count_pending_suggestions() == 3
    assert repo.count_automatic_suggestions() == 10


def test_fetch_commercial_entities_maps_records() -> None:
    entity = BusinessEntityMaster(
        entity_id=1,
        entity_code="C0027",
        entity_name="WALMART",
        source_system="D365_FO",
        source_table="movimientos_diario",
        source_column="cuenta_cliente",
        movement_count=1,
        movement_amount=Decimal("1"),
        first_seen=None,
        last_seen=None,
        classification_status="pending",
        confidence=None,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    session = MagicMock(spec=Session)
    session.scalars.return_value.all.return_value = [entity]
    repo = CanonicalBusinessEntityRepository(session)
    records = repo.fetch_commercial_entities()
    assert len(records) == 1
    assert records[0].entity_code == "C0027"


def test_get_unresolved_commercial_entity_ids() -> None:
    session = MagicMock(spec=Session)
    session.execute.return_value.fetchall.return_value = [(1,), (2,)]
    repo = CanonicalBusinessEntityRepository(session)
    assert repo.get_unresolved_commercial_entity_ids() == [1, 2]


def test_create_singleton_canonical_persists() -> None:
    session = MagicMock(spec=Session)

    def _assign_id(obj) -> None:
        if isinstance(obj, CanonicalBusinessEntity):
            obj.canonical_id = 99

    session.add.side_effect = _assign_id
    session.flush.side_effect = None

    entity = BusinessEntityMaster(
        entity_id=7,
        entity_code="NWM9709244",
        entity_name="NUEVA WALMART DE MEXICO S DE RL DE CV",
        source_system="D365_FO",
        source_table="movimientos_diario",
        source_column="cuenta_proveedor",
        movement_count=1,
        movement_amount=Decimal("1"),
        first_seen=None,
        last_seen=None,
        classification_status="pending",
        confidence=None,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    repo = CanonicalBusinessEntityRepository(session)
    canonical, resolution = repo.create_singleton_canonical(entity, now=datetime(2026, 6, 24))
    assert canonical.canonical_id == 99
    assert resolution.entity_id == 7
    assert resolution.resolution_rule == "singleton_bootstrap"


def test_upsert_suggestion_inserts_new() -> None:
    session = MagicMock(spec=Session)
    session.scalar.return_value = None
    repo = CanonicalBusinessEntityRepository(session)
    inserted = repo.upsert_suggestion(
        source_entity_id=1,
        candidate_entity_id=2,
        rule_used="brand_token_match",
        score=Decimal("0.8800"),
        now=datetime(2026, 6, 24),
    )
    assert inserted is True
    session.add.assert_called_once()


def test_upsert_suggestion_updates_higher_score() -> None:
    existing = CanonicalEntitySuggestion(
        suggestion_id=1,
        source_entity_id=1,
        candidate_entity_id=2,
        rule_used="token_overlap",
        score=Decimal("0.7000"),
        status="pending",
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    session = MagicMock(spec=Session)
    session.scalar.return_value = existing
    repo = CanonicalBusinessEntityRepository(session)
    inserted = repo.upsert_suggestion(
        source_entity_id=1,
        candidate_entity_id=2,
        rule_used="token_overlap",
        score=Decimal("0.8500"),
        now=datetime(2026, 6, 24),
    )
    assert inserted is False
    assert existing.score == Decimal("0.8500")


def test_list_canonical_with_search() -> None:
    canonical = CanonicalBusinessEntity(
        canonical_id=1,
        canonical_name="WALMART",
        normalized_name="WALMART",
        primary_rfc="NWM9709244",
        alias_count=1,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    session = MagicMock(spec=Session)
    session.scalar.return_value = 1
    session.scalars.return_value.all.return_value = [canonical]
    repo = CanonicalBusinessEntityRepository(session)
    rows, total = repo.list_canonical(search="walmart", page=1, page_size=10)
    assert total == 1
    assert rows[0].canonical_name == "WALMART"


def test_list_aliases_for_canonical() -> None:
    session = MagicMock(spec=Session)
    session.execute.return_value.mappings.return_value.all.return_value = [
        {
            "entity_id": 1,
            "entity_code": "C0027",
            "entity_name": "WALMART",
            "source_column": "cuenta_cliente",
            "resolution_rule": "singleton_bootstrap",
            "resolution_score": Decimal("1.0000"),
        }
    ]
    repo = CanonicalBusinessEntityRepository(session)
    aliases = repo.list_aliases_for_canonical(1)
    assert aliases[0]["entity_code"] == "C0027"


def test_list_suggestions_returns_rows() -> None:
    session = MagicMock(spec=Session)
    session.execute.return_value.scalar_one.return_value = 1
    session.execute.return_value.mappings.return_value.all.return_value = [
        {
            "suggestion_id": 1,
            "rule_used": "brand_token_match",
            "score": Decimal("0.8800"),
            "status": "pending",
            "created_at": datetime(2026, 1, 1),
            "source_entity_id": 1,
            "source_entity_code": "C0027",
            "source_entity_name": "WALMART",
            "source_source_column": "cuenta_cliente",
            "candidate_entity_id": 2,
            "candidate_entity_code": "NWM9709244",
            "candidate_entity_name": "NUEVA WALMART",
            "candidate_source_column": "cuenta_proveedor",
        }
    ]
    repo = CanonicalBusinessEntityRepository(session)
    rows, total = repo.list_suggestions(status="pending", min_score=0.8)
    assert total == 1
    assert rows[0]["rule_used"] == "brand_token_match"


def test_find_health_issues_returns_all_buckets() -> None:
    session = MagicMock(spec=Session)
    session.execute.return_value.mappings.return_value.all.side_effect = [
        [{"entity_id": 1}],
        [],
        [],
        [],
    ]
    repo = CanonicalBusinessEntityRepository(session)
    issues = repo.find_health_issues()
    assert len(issues["orphan_entities"]) == 1
    assert issues["duplicate_resolutions"] == []
