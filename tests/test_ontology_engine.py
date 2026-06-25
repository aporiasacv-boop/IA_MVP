from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

from app.business_ontology.metrics import BusinessOntologyMetrics
from app.business_ontology.ontology_engine import OntologyEngine


def test_engine_run_idempotent() -> None:
    BusinessOntologyMetrics.reset_for_tests()
    repo = MagicMock()
    repo.seed_taxonomy_if_empty.return_value = 35
    repo.seed_rules_if_empty.return_value = 25
    repo.get_type_code_map.return_value = {("role", "CLIENTE"): 10}
    repo.fetch_active_rules.return_value = [
        {
            "rule_code": "role_client_dimension",
            "concept_category": "role",
            "type_code": "CLIENTE",
            "conditions_json": {"requires_only_dimension": "cuenta_cliente"},
            "score_weight": Decimal("0.92"),
            "target_type_id": 10,
        }
    ]
    repo.fetch_entity_contexts.return_value = [
        {
            "canonical_id": 1,
            "canonical_name": "WALMART",
            "primary_rfc": None,
            "normalized_name": "WALMART",
            "alias_count": 1,
            "total_movements": 100,
            "total_amount": Decimal("1000"),
            "debit_amount": Decimal("600"),
            "credit_amount": Decimal("400"),
            "debit_credit_ratio": Decimal("1.5"),
            "related_accounts_count": 2,
            "related_counterparties_count": 1,
            "active_months": 6,
            "dimensions_used": ["cuenta_cliente"],
            "top_accounts": [],
            "top_counterparties": [],
            "currencies": ["MXN"],
        }
    ]
    repo.upsert_assignment.return_value = True
    repo.count_entities_with_assignments.return_value = 1
    repo.count_assignments.return_value = 1
    repo.count_rules.return_value = 25
    repo.average_confidence.return_value = 0.85

    engine = OntologyEngine(repo)
    result = engine.run_idempotent(now=datetime(2026, 6, 24))
    assert result.entities_processed == 1
    assert result.suggestions_inserted >= 1
    repo.session.commit.assert_called_once()
