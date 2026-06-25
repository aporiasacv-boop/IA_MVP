import pytest

from app.knowledge_pack.loader import clear_knowledge_pack_cache, list_by_category, search_items


@pytest.fixture(autouse=True)
def reset_cache() -> None:
    clear_knowledge_pack_cache()


def test_concepts_count() -> None:
    items = list_by_category("concepts")
    assert len(items) == 30


def test_rules_count() -> None:
    items = list_by_category("rules")
    assert len(items) >= 40


def test_faq_exists() -> None:
    items = list_by_category("faq")
    assert len(items) >= 1
    assert "preguntas" in items[0].content.lower()


def test_glossary_terms_count() -> None:
    items = list_by_category("glossary")
    assert len(items) >= 1
    assert items[0].content.count("## ") >= 50


def test_scenarios_count() -> None:
    items = list_by_category("scenarios")
    assert len(items) == 20


def test_search_cliente() -> None:
    results = search_items("cliente")
    assert results
    assert any("cliente" in item.title.lower() or "cliente" in item.content.lower() for item in results)


def test_examples_use_real_entities() -> None:
    items = list_by_category("examples")
    text = "\n".join(item.content for item in items)
    assert "PUBLICO EN GENERAL" in text
    assert "WALMART" in text
    assert "COSTCO" in text
    assert "NOMINA POR PAGAR" in text
