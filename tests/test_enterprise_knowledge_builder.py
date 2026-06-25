from datetime import datetime
from decimal import Decimal

from app.enterprise_knowledge.knowledge_builder import build_enterprise_knowledge_object


def test_build_eko_with_profile_and_ontology() -> None:
    computed_at = datetime(2026, 6, 24, 12, 0, 0)
    eko = build_enterprise_knowledge_object(
        canonical={
            "canonical_id": 1,
            "canonical_name": "WALMART",
            "normalized_name": "WALMART",
            "primary_rfc": "NWM9709244",
            "alias_count": 2,
        },
        aliases=[
            {
                "entity_id": 10,
                "entity_code": "C0027",
                "entity_name": "WALMART",
                "source_column": "cuenta_cliente",
                "resolution_rule": "singleton_bootstrap",
                "resolution_score": Decimal("1.0000"),
            }
        ],
        profile={
            "profile_id": 1,
            "total_movements": 150,
            "total_amount": Decimal("50000"),
            "average_amount": Decimal("333.33"),
            "debit_amount": Decimal("30000"),
            "credit_amount": Decimal("20000"),
            "debit_credit_ratio": Decimal("1.5"),
            "active_months": 6,
            "active_days": 120,
            "related_accounts_count": 3,
            "related_counterparties_count": 2,
            "first_seen": "2024-01-01",
            "last_seen": "2024-12-01",
            "currencies": ["MXN"],
            "dimensions_used": ["cuenta_cliente"],
            "profile_completeness": Decimal("0.85"),
            "monthly_distribution": {"2024-01": {"movements": 10, "amount": 5000}},
            "top_accounts": [{"code": "40101", "name": "VENTAS", "movements": 50, "amount": 25000}],
            "top_counterparties": [],
        },
        ontology_assignments=[
            {
                "assignment_id": 1,
                "concept_category": "role",
                "type_code": "CLIENTE",
                "type_label": "Cliente",
                "rule_code": "role_client_dimension",
                "evidence_json": {"only_dimension": "cuenta_cliente"},
                "score": Decimal("0.92"),
                "confidence": Decimal("0.88"),
                "status": "pending",
            }
        ],
        computed_at=computed_at,
    )
    assert eko.canonical_id == 1
    assert len(eko.facts) >= 5
    assert len(eko.roles) == 1
    assert eko.metadata["contains_sql"] is False
    assert eko.metadata["contains_llm_output"] is False
    assert float(eko.quality.completeness) > 0


def test_build_eko_signals_and_alerts() -> None:
    computed_at = datetime(2026, 6, 24)
    eko = build_enterprise_knowledge_object(
        canonical={
            "canonical_id": 3,
            "canonical_name": "TEST",
            "normalized_name": "TEST",
            "primary_rfc": None,
            "alias_count": 1,
        },
        aliases=[],
        profile={
            "profile_id": 1,
            "total_movements": 0,
            "total_amount": Decimal("0"),
            "debit_credit_ratio": Decimal("0.3"),
            "profile_completeness": Decimal("0.5"),
            "monthly_distribution": {
                "2024-01": {"amount": 100},
                "2024-02": {"amount": 10},
                "2024-03": {"amount": 5},
            },
            "top_counterparties": [{"code": "CP1", "name": "Prov", "dimension": "cuenta_proveedor"}],
        },
        ontology_assignments=[
            {"assignment_id": 1, "concept_category": "role", "type_code": "CLIENTE", "type_label": "C", "rule_code": "r1", "evidence_json": {}, "confidence": Decimal("0.8"), "status": "pending"},
            {"assignment_id": 2, "concept_category": "role", "type_code": "PROVEEDOR", "type_label": "P", "rule_code": "r2", "evidence_json": {}, "confidence": Decimal("0.7"), "status": "pending"},
            {"assignment_id": 3, "concept_category": "role", "type_code": "OTRO", "type_label": "O", "rule_code": "r3", "evidence_json": {}, "confidence": Decimal("0.6"), "status": "pending"},
            {"assignment_id": 4, "concept_category": "nature", "type_code": "ACTIVO", "type_label": "A", "rule_code": "r4", "evidence_json": {}, "confidence": Decimal("0.9"), "status": "pending"},
            {"assignment_id": 5, "concept_category": "nature", "type_code": "PASIVO", "type_label": "P", "rule_code": "r5", "evidence_json": {}, "confidence": Decimal("0.85"), "status": "pending"},
            {"assignment_id": 6, "concept_category": "behavior", "type_code": "RECURRENTE", "type_label": "R", "rule_code": "r6", "evidence_json": {}, "confidence": Decimal("0.75"), "status": "pending"},
            {"assignment_id": 7, "concept_category": "identity", "type_code": "PERSONA_MORAL", "type_label": "PM", "rule_code": "r7", "evidence_json": {}, "confidence": Decimal("0.95"), "status": "pending"},
        ],
        computed_at=computed_at,
    )
    alert_keys = {a.key for a in eko.alerts}
    assert "no_movements" in alert_keys
    assert "ambiguous_roles" in alert_keys
    assert "conflicting_natures" in alert_keys
    signal_keys = {s.key for s in eko.signals}
    assert "credit_dominant" in signal_keys
    assert "seasonal_peak" in signal_keys
    assert len(eko.behaviors) == 1
    assert len(eko.relationships) == 1

    eko = build_enterprise_knowledge_object(
        canonical={
            "canonical_id": 2,
            "canonical_name": "EMPTY",
            "normalized_name": "EMPTY",
            "primary_rfc": None,
            "alias_count": 1,
        },
        aliases=[],
        profile=None,
        ontology_assignments=[],
        computed_at=datetime(2026, 6, 24),
    )
    alert_keys = {a.key for a in eko.alerts}
    assert "missing_profile" in alert_keys
    assert "missing_ontology" in alert_keys
