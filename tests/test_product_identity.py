"""Pruebas del módulo de identidad de producto."""

from app.product_identity.matcher import build_identity_answer, is_identity_question
from app.product_identity.profile import get_product_identity
from app.product_identity.responder import (
    HANDLED_BY_PRODUCT_IDENTITY,
    try_product_identity_response,
)


def test_official_identity_name() -> None:
    profile = get_product_identity()
    assert profile.name == "Olnatura Intelligence"


def test_identity_question_como_te_llamas() -> None:
    answer = build_identity_answer("¿Cómo te llamas?")
    assert answer is not None
    assert "Olnatura Intelligence" in answer


def test_identity_question_quien_eres() -> None:
    answer = build_identity_answer("¿Quién eres?")
    assert answer is not None
    assert "Olnatura Intelligence" in answer


def test_identity_question_quien_te_creo() -> None:
    answer = build_identity_answer("¿Quién te creó?")
    assert answer is not None
    assert "desarrollado" in answer.lower()


def test_capabilities_question() -> None:
    answer = build_identity_answer("¿Qué puedes hacer?")
    assert answer is not None
    assert "clientes" in answer.lower()
    assert "proveedores" in answer.lower()


def test_information_source_question() -> None:
    answer = build_identity_answer("¿Cómo obtienes la información?")
    assert answer is not None
    assert "datos corporativos" in answer.lower()


def test_non_identity_question_returns_none() -> None:
    assert build_identity_answer("¿Cuántos clientes existen?") is None
    assert not is_identity_question("¿Cuántos clientes existen?")


def test_try_product_identity_response() -> None:
    result = try_product_identity_response("¿Cómo te llamas?")
    assert result is not None
    assert result.handled_by == HANDLED_BY_PRODUCT_IDENTITY
    assert result.success is True
    assert "Olnatura Intelligence" in result.answer
    assert result.metadata["confidence"] == 1.0


def test_try_product_identity_response_none_for_business_query() -> None:
    assert try_product_identity_response("¿Cuántos proveedores hay?") is None
