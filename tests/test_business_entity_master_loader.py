from datetime import datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock

from app.business_entity_master.loader import BusinessEntityMasterLoader
from app.business_entity_master.metrics import BusinessEntityMasterMetrics


def test_load_idempotent_records_metrics() -> None:
    BusinessEntityMasterMetrics.reset_for_tests()
    session = MagicMock()
    repo = MagicMock()
    repo.fetch_discovered_entities.return_value = [
        {
            "entity_code": "20101001",
            "entity_name": "PROVEEDORES",
            "source_column": "account_display_value",
            "movement_count": 1,
            "movement_amount": Decimal("1"),
            "first_seen": None,
            "last_seen": None,
        }
    ]
    repo.upsert_entity.return_value = (MagicMock(), True)
    repo.count_all.return_value = 1
    repo.count_duplicated_codes.return_value = 0
    repo.get_by_code.return_value = []
    repo.session = session

    loader = BusinessEntityMasterLoader(repo)
    result = loader.load_idempotent(now=datetime(2026, 6, 23, 10, 0, 0))

    assert result.inserted == 1
    assert result.total_processed == 1
    assert BusinessEntityMasterMetrics.business_entities_loaded == 1
    assert BusinessEntityMasterMetrics.last_entity_refresh is not None


def test_load_idempotent_with_csv(tmp_path: Path) -> None:
    BusinessEntityMasterMetrics.reset_for_tests()
    repo = MagicMock()
    repo.fetch_discovered_entities.return_value = []
    repo.upsert_entity.return_value = (MagicMock(), True)
    repo.count_all.return_value = 0
    repo.count_duplicated_codes.return_value = 0
    repo.get_by_code.return_value = []
    repo.session = MagicMock()

    csv_path = tmp_path / "catalog.csv"
    csv_path.write_text(
        "codigo,nombre,cantidad_movimientos,monto_total,grupo_sugerido,confianza,observaciones\n"
        "20401001,NOMINA,1,1,x,alta,Fuentes: proveedor_dim\n",
        encoding="utf-8",
    )

    loader = BusinessEntityMasterLoader(repo)
    loader.load_idempotent(csv_path=csv_path, now=datetime(2026, 1, 1))
    repo.get_by_code.assert_called()


def test_merge_csv_confidence_updates_existing(tmp_path: Path) -> None:
    session = MagicMock()
    repo = MagicMock()
    entity = MagicMock()
    repo.get_by_code.return_value = [entity]
    repo.session = session

    loader = BusinessEntityMasterLoader(repo)
    path = tmp_path / "entity.csv"
    path.write_text(
        "codigo,nombre,cantidad_movimientos,monto_total,grupo_sugerido,confianza,observaciones\n"
        "20401001,NOMINA,1,1,x,alta,Fuentes: proveedor_dim\n",
        encoding="utf-8",
    )
    loader._merge_csv_confidence(path, timestamp=datetime(2026, 1, 1))
    assert entity.confidence == "alta"
    session.commit.assert_called_once()
