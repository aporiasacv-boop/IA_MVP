import pytest

from app.canonical_business_entity.matcher import EntityRecord, generate_match_candidates
from app.canonical_business_entity.normalizer import (
    extract_rfc,
    fuzzy_name_score,
    normalize_organization_name,
    token_overlap_score,
)


def test_normalize_organization_name_strips_legal_suffix() -> None:
    normalized = normalize_organization_name("NUEVA WALMART DE MEXICO S DE RL DE CV")
    assert "WALMART" in normalized
    assert "S DE RL" not in normalized


def test_extract_rfc_from_code() -> None:
    assert extract_rfc("NWM9709244", "NUEVA WALMART") == "NWM9709244"


def test_token_overlap_detects_walmart() -> None:
    left = normalize_organization_name("NUEVA WAL MART DE MEXICO")
    right = normalize_organization_name("WALMART MEXICO")
    assert token_overlap_score(left, right) >= 0.3


def test_generate_match_candidates_walmart_pair() -> None:
    entities = [
        EntityRecord(1, "C0027", "NUEVA WAL MART DE MEXICO", "cuenta_cliente"),
        EntityRecord(2, "NWM9709244", "NUEVA WALMART DE MEXICO S DE RL DE CV", "cuenta_proveedor"),
    ]
    matches = generate_match_candidates(entities)
    assert len(matches) >= 1
    assert any(match.source_entity_id in {1, 2} for match in matches)


def test_generate_match_candidates_rfc_exact() -> None:
    entities = [
        EntityRecord(1, "NWM970924ABC", "PROVEEDOR A", "cuenta_proveedor"),
        EntityRecord(2, "NWM970924ABC", "PROVEEDOR B", "cuenta_cliente"),
    ]
    matches = generate_match_candidates(entities)
    assert any(match.rule_used == "rfc_exact" for match in matches)


def test_generate_match_candidates_skips_low_scores() -> None:
    entities = [
        EntityRecord(1, "A001", "ALPHA CORP", "cuenta_cliente"),
        EntityRecord(2, "B002", "BETA INDUSTRIES", "cuenta_proveedor"),
    ]
    matches = generate_match_candidates(entities)
    assert matches == []


def test_brand_token_match_walmart() -> None:
    from app.canonical_business_entity.normalizer import brand_token_score

    left = normalize_organization_name("NUEVA WAL MART DE MEXICO")
    right = normalize_organization_name("WALMART MEXICO")
    assert brand_token_score(left, right) >= 0.88
