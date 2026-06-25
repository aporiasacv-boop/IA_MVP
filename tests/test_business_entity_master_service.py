from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.business_entity_master.constants import (
    CLASSIFICATION_PENDING,
    SOURCE_COLUMN_ACCOUNT,
    SOURCE_SYSTEM_D365,
    SOURCE_TABLE_MOVIMIENTOS,
)
from app.business_entity_master.loader import BusinessEntityMasterLoader
from app.business_entity_master.metrics import BusinessEntityMasterMetrics
from app.business_entity_master.repository import BusinessEntityMasterRepository
from app.business_entity_master.service import BusinessEntityMasterService
from app.models.business_entity_master import BusinessEntityMaster


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    BusinessEntityMasterMetrics.reset_for_tests()


def test_loader_resolve_source_column() -> None:
    assert BusinessEntityMasterLoader._resolve_source_column("Fuentes: cuenta_contable") == "account_display_value"
    assert BusinessEntityMasterLoader._resolve_source_column("Fuentes: proveedor_dim") == "cuenta_proveedor"
    assert BusinessEntityMasterLoader._resolve_source_column("sin fuente") is None


def test_loader_upsert_batch_counts_insert_and_update() -> None:
    session = MagicMock()
    repo = BusinessEntityMasterRepository(session)
    repo.count_duplicated_codes = MagicMock(return_value=0)
    repo.upsert_entity = MagicMock(side_effect=[(MagicMock(), True), (MagicMock(), False)])
    loader = BusinessEntityMasterLoader(repo)
    now = datetime(2026, 6, 23, 12, 0, 0)
    rows = [
        {
            "entity_code": "20101001",
            "entity_name": "PROVEEDORES",
            "source_column": SOURCE_COLUMN_ACCOUNT,
            "movement_count": 10,
            "movement_amount": Decimal("100.50"),
            "first_seen": date(2025, 1, 1),
            "last_seen": date(2025, 12, 31),
        },
        {
            "entity_code": "C0003",
            "entity_name": "PUBLICO EN GENERAL",
            "source_column": "cuenta_cliente",
            "movement_count": 5,
            "movement_amount": Decimal("50"),
            "first_seen": date(2025, 1, 1),
            "last_seen": date(2025, 6, 1),
        },
    ]
    result = loader._upsert_batch(rows, timestamp=now)
    assert result.inserted == 1
    assert result.updated == 1
    assert result.total_processed == 2
    session.commit.assert_called_once()


def test_service_list_entities_maps_response() -> None:
    entity = BusinessEntityMaster(
        entity_id=1,
        entity_code="20401001",
        entity_name="NOMINA POR PAGAR",
        source_system=SOURCE_SYSTEM_D365,
        source_table=SOURCE_TABLE_MOVIMIENTOS,
        source_column="cuenta_proveedor",
        movement_count=100,
        movement_amount=Decimal("1000"),
        first_seen=date(2025, 1, 1),
        last_seen=date(2025, 12, 31),
        classification_status=CLASSIFICATION_PENDING,
        confidence=None,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    repo = MagicMock(spec=BusinessEntityMasterRepository)
    repo.list_entities.return_value = ([entity], 1)
    service = BusinessEntityMasterService(repo)

    response = service.list_entities(search="nomina", page=1, page_size=10)
    assert response.total == 1
    assert response.items[0].entity_code == "20401001"
    repo.list_entities.assert_called_once()


def test_service_validate_health_delegates() -> None:
    repo = MagicMock(spec=BusinessEntityMasterRepository)
    repo.find_health_issues.return_value = {
        "duplicated_codes": [],
        "empty_names": [],
        "inconsistent_dates": [],
        "inconsistent_amounts": [],
    }
    service = BusinessEntityMasterService(repo)
    result = service.validate_health()
    assert result["status"] == "healthy"


def test_loader_load_from_csv_parses_rows(tmp_path: Path) -> None:
    session = MagicMock()
    repo = MagicMock()
    repo.upsert_entity.return_value = (MagicMock(), True)
    repo.count_duplicated_codes.return_value = 0
    repo.session = session

    path = tmp_path / "catalog.csv"
    path.write_text(
        "codigo,nombre,cantidad_movimientos,monto_total,grupo_sugerido,confianza,observaciones\n"
        "20401001,NOMINA,10,100.5,x,alta,Fuentes: proveedor_dim\n",
        encoding="utf-8",
    )

    loader = BusinessEntityMasterLoader(repo)
    result = loader.load_from_csv(path, now=datetime(2026, 1, 1))
    assert result.inserted == 1
    repo.upsert_entity.assert_called_once()


def test_service_get_by_code_maps_items() -> None:
    entity = BusinessEntityMaster(
        entity_id=2,
        entity_code="20401001",
        entity_name="NOMINA",
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
    repo = MagicMock(spec=BusinessEntityMasterRepository)
    repo.get_by_code.return_value = [entity]
    service = BusinessEntityMasterService(repo)
    items = service.get_by_code("20401001")
    assert len(items) == 1
    assert items[0].entity_name == "NOMINA"


def test_service_load_idempotent_delegates() -> None:
    repo = MagicMock(spec=BusinessEntityMasterRepository)
    service = BusinessEntityMasterService(repo)
    service._loader.load_idempotent = MagicMock(
        return_value=MagicMock(inserted=1, updated=2, total_processed=3, duplicated_entity_codes=0)
    )
    result = service.load_idempotent()
    assert result.total_processed == 3


def test_service_get_health_issues() -> None:
    repo = MagicMock(spec=BusinessEntityMasterRepository)
    repo.find_health_issues.return_value = {"duplicated_codes": []}
    service = BusinessEntityMasterService(repo)
    assert service.get_health_issues() == {"duplicated_codes": []}


def test_service_get_statistics_uses_metrics_snapshot() -> None:
    repo = MagicMock(spec=BusinessEntityMasterRepository)
    repo.count_all.return_value = 100
    repo.count_duplicated_codes.return_value = 3
    repo.get_statistics_breakdown.return_value = ({"cuenta_proveedor": 10}, {"pending": 100})
    BusinessEntityMasterMetrics.record_refresh(loaded=50, duplicated=3)

    service = BusinessEntityMasterService(repo)
    stats = service.get_statistics()
    assert stats.business_entities_total == 100
    assert stats.business_entities_loaded == 50
    assert stats.duplicated_entities == 3
    assert stats.by_source_column["cuenta_proveedor"] == 10
