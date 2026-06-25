from app.canonical_business_entity.normalizer import (
    brand_tokens,
    extract_rfc,
    fuzzy_name_score,
    significant_tokens,
    strip_accents,
)


def test_strip_accents() -> None:
    assert strip_accents("México") == "Mexico"


def test_extract_rfc_full_from_name() -> None:
    assert extract_rfc("X", "RFC NWM970924ABC proveedor") == "NWM970924ABC"


def test_significant_tokens_includes_compact_form() -> None:
    tokens = significant_tokens("NUEVA WAL MART DE MEXICO")
    assert "WALMART" in tokens


def test_brand_tokens_filters_short() -> None:
    assert "WAL" not in brand_tokens("WAL MART")
    assert "WALMART" in brand_tokens("WALMART MEXICO")


def test_fuzzy_name_score_empty() -> None:
    assert fuzzy_name_score("", "WALMART") == 0.0
