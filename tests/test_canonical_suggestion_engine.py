from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

from app.canonical_business_entity.matcher import EntityRecord
from app.canonical_business_entity.metrics import CanonicalEntityMetrics
from app.canonical_business_entity.suggestion_engine import CanonicalSuggestionEngine
from app.models.business_entity_master import BusinessEntityMaster


def test_suggestion_engine_creates_singletons_and_suggestions() -> None:
    CanonicalEntityMetrics.reset_for_tests()
    repo = MagicMock()
    entity = BusinessEntityMaster(
        entity_id=1,
        entity_code="C0027",
        entity_name="NUEVA WAL MART DE MEXICO",
        source_system="D365_FO",
        source_table="movimientos_diario",
        source_column="cuenta_cliente",
        movement_count=10,
        movement_amount=Decimal("100"),
        first_seen=None,
        last_seen=None,
        classification_status="pending",
        confidence=None,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    repo.get_unresolved_commercial_entity_ids.side_effect = [[1], []]
    repo.session.scalars.return_value.all.return_value = [entity]
    repo.create_singleton_canonical.return_value = (MagicMock(), MagicMock())
    repo.fetch_commercial_entities.return_value = [
        EntityRecord(1, "C0027", "NUEVA WAL MART DE MEXICO", "cuenta_cliente"),
        EntityRecord(2, "NWM9709244", "NUEVA WALMART DE MEXICO S DE RL DE CV", "cuenta_proveedor"),
    ]
    repo.upsert_suggestion.return_value = True
    repo.count_canonical.return_value = 1
    repo.count_canonical_matches.return_value = 0
    repo.count_pending_suggestions.return_value = 1
    repo.count_automatic_suggestions.return_value = 1

    engine = CanonicalSuggestionEngine(repo)
    result = engine.run_idempotent(now=datetime(2026, 6, 24))
    assert result.singletons_created == 1
    assert result.suggestions_inserted >= 1
    repo.session.commit.assert_called()
