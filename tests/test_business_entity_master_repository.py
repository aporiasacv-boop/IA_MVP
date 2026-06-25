from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from app.business_entity_master.repository import BusinessEntityMasterRepository
from app.models.business_entity_master import BusinessEntityMaster


def _scalar_session(return_value):
    session = MagicMock(spec=Session)
    session.scalar.return_value = return_value
    return session


def test_count_all_returns_zero_when_empty() -> None:
    repo = BusinessEntityMasterRepository(_scalar_session(0))
    assert repo.count_all() == 0


def test_get_by_code_returns_rows() -> None:
    entity = BusinessEntityMaster(
        entity_id=1,
        entity_code="C0003",
        entity_name="PUBLICO EN GENERAL",
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
    repo = BusinessEntityMasterRepository(session)
    rows = repo.get_by_code("C0003")
    assert len(rows) == 1
    assert rows[0].entity_code == "C0003"


def test_upsert_entity_inserts_when_missing() -> None:
    session = MagicMock(spec=Session)
    session.scalar.return_value = None
    repo = BusinessEntityMasterRepository(session)
    entity, is_new = repo.upsert_entity(
        entity_code="20101001",
        entity_name="PROVEEDORES",
        source_system="D365_FO",
        source_table="movimientos_diario",
        source_column="account_display_value",
        movement_count=10,
        movement_amount=Decimal("100"),
        first_seen=date(2025, 1, 1),
        last_seen=date(2025, 12, 31),
        classification_status="pending",
        confidence=None,
        now=datetime(2026, 1, 1),
    )
    assert is_new is True
    session.add.assert_called_once()
    assert entity.entity_code == "20101001"


def test_count_duplicated_codes_reads_sql() -> None:
    session = MagicMock(spec=Session)
    session.execute.return_value.mappings.return_value.one.return_value = {"duplicated": 4}
    repo = BusinessEntityMasterRepository(session)
    assert repo.count_duplicated_codes() == 4


def test_list_entities_applies_filters() -> None:
    session = MagicMock(spec=Session)
    session.scalar.return_value = 2
    session.scalars.return_value.all.return_value = []
    repo = BusinessEntityMasterRepository(session)
    rows, total = repo.list_entities(
        search="nomina",
        source_column="cuenta_proveedor",
        classification_status="pending",
        sort_by="entity_name",
        sort_dir="asc",
        page=2,
        page_size=25,
    )
    assert rows == []
    assert total == 2


def test_get_statistics_breakdown() -> None:
    session = MagicMock(spec=Session)
    session.execute.side_effect = [
        MagicMock(all=lambda: [("account_display_value", 10)]),
        MagicMock(all=lambda: [("pending", 10)]),
    ]
    repo = BusinessEntityMasterRepository(session)
    by_source, by_status = repo.get_statistics_breakdown()
    assert by_source["account_display_value"] == 10
    assert by_status["pending"] == 10


def test_find_health_issues_returns_buckets() -> None:
    session = MagicMock(spec=Session)
    session.execute.return_value.mappings.return_value.all.side_effect = [
        [{"entity_code": "X", "occurrences": 2}],
        [],
        [],
        [],
    ]
    repo = BusinessEntityMasterRepository(session)
    issues = repo.find_health_issues()
    assert issues["duplicated_codes"][0]["entity_code"] == "X"
    assert issues["empty_names"] == []


def test_fetch_discovered_entities_maps_three_sources() -> None:
    session = MagicMock(spec=Session)
    row = {
        "entity_code": "20101001",
        "entity_name": "PROVEEDORES",
        "movement_count": 5,
        "movement_amount": Decimal("10"),
        "first_seen": date(2025, 1, 1),
        "last_seen": date(2025, 12, 31),
    }
    session.execute.return_value.mappings.return_value.all.return_value = [row]
    repo = BusinessEntityMasterRepository(session)
    discovered = repo.fetch_discovered_entities()
    assert len(discovered) == 3
    assert discovered[0]["source_column"] == "account_display_value"


def test_upsert_entity_updates_when_exists() -> None:
    existing = BusinessEntityMaster(
        entity_id=9,
        entity_code="20101001",
        entity_name="OLD",
        source_system="D365_FO",
        source_table="movimientos_diario",
        source_column="account_display_value",
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
    session.scalar.return_value = existing
    repo = BusinessEntityMasterRepository(session)
    entity, is_new = repo.upsert_entity(
        entity_code="20101001",
        entity_name="PROVEEDORES",
        source_system="D365_FO",
        source_table="movimientos_diario",
        source_column="account_display_value",
        movement_count=99,
        movement_amount=Decimal("999"),
        first_seen=date(2025, 1, 1),
        last_seen=date(2025, 12, 31),
        classification_status="pending",
        confidence="alta",
        now=datetime(2026, 6, 1),
    )
    assert is_new is False
    assert entity.movement_count == 99
    assert entity.confidence == "alta"
    session.add.assert_not_called()
