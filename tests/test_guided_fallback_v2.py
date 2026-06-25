import pytest

from app.guided_fallback.engine import GuidedFallbackEngine
from app.guided_fallback.types import FallbackType
from app.guided_fallback.v2.detector import detect_domain
from app.guided_fallback.v2.domains import BusinessDomain, DOMAIN_HINTS, SUPPORTED_CAPABILITIES
from app.guided_fallback.v2.formatter import build_domain_contextual_answer
from app.guided_fallback.v2.metrics import GuidedFallbackV2Metrics
from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_types import BusinessQueryType
from app.schemas.semantic_intent import BusinessFilters, BusinessSemanticIntent


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    GuidedFallbackV2Metrics.reset()


@pytest.fixture
def engine() -> GuidedFallbackEngine:
    return GuidedFallbackEngine(
        top_questions_provider=lambda limit: [
            "¿Cuántos clientes existen?",
        ][:limit],
    )


def _unsupported_intent() -> BusinessSemanticIntent:
    return BusinessSemanticIntent(
        operation=None,
        target_entity=None,
        source_entity=None,
        filters=BusinessFilters(),
        confidence=0.2,
        source_question="",
    )


@pytest.mark.parametrize(
    ("question", "expected"),
    [
        ("¿Cómo van las ventas?", BusinessDomain.VENTAS),
        ("¿Cómo van las compras?", BusinessDomain.COMPRAS),
        ("¿Cómo está el inventario?", BusinessDomain.INVENTARIO),
        ("¿Cuál es la facturación del mes?", BusinessDomain.FACTURACION),
        ("¿Qué información financiera tienes?", BusinessDomain.FINANZAS),
        ("venta del trimestre", BusinessDomain.VENTAS),
        ("stock disponible", BusinessDomain.INVENTARIO),
    ],
)
def test_detect_domain(question: str, expected: BusinessDomain) -> None:
    assert detect_domain(question) == expected


def test_detect_domain_returns_none_without_hints() -> None:
    assert detect_domain("¿Cómo va el negocio?") is None
    assert detect_domain("hola equipo") is None


def test_domain_hints_cover_required_domains() -> None:
    required = {
        BusinessDomain.VENTAS,
        BusinessDomain.COMPRAS,
        BusinessDomain.INVENTARIO,
        BusinessDomain.FACTURACION,
        BusinessDomain.FINANZAS,
        BusinessDomain.LOGISTICA,
        BusinessDomain.PRODUCCION,
    }
    assert set(DOMAIN_HINTS.keys()) == required


def test_build_domain_contextual_answer_limits_capabilities() -> None:
    answer = build_domain_contextual_answer(BusinessDomain.VENTAS)
    assert answer.startswith("Detecté una consulta relacionada con ventas.")
    assert "Actualmente no dispongo de información de ventas." in answer
    assert "Puedo ayudarte con información sobre:" in answer
    assert "¿Qué puedes hacer?" not in answer
    assert "Rankings" not in answer
    assert answer.count("•") == len(SUPPORTED_CAPABILITIES) == 4


def test_resolve_uses_domain_context_for_ventas(engine: GuidedFallbackEngine) -> None:
    result = engine.resolve(
        "¿Cómo van las ventas?",
        _unsupported_intent(),
        BusinessQuery(query_type=BusinessQueryType.UNSUPPORTED, filters={}),
        None,
    )
    assert result is not None
    assert "Detecté una consulta relacionada con ventas." in result.answer
    assert result.metadata["domain_detected"] == BusinessDomain.VENTAS.value
    assert result.metadata["domain_contextual"] is True
    snapshot = GuidedFallbackV2Metrics.snapshot()
    assert snapshot["domain_fallback_hits"] == 1
    assert snapshot["domain_detected"] == BusinessDomain.VENTAS.value


def test_resolve_keeps_v1_for_negocio_ambiguous(engine: GuidedFallbackEngine) -> None:
    result = engine.resolve(
        "¿Cómo va el negocio?",
        _unsupported_intent(),
        BusinessQuery(query_type=BusinessQueryType.UNSUPPORTED, filters={}),
        None,
    )
    assert result is not None
    assert result.fallback_type == FallbackType.AMBIGUOUS.value
    assert "Detecté una consulta relacionada con" not in result.answer
    assert result.metadata["domain_detected"] is None
    assert GuidedFallbackV2Metrics.snapshot()["domain_fallback_misses"] == 1


def test_resolve_keeps_out_of_domain_without_context(engine: GuidedFallbackEngine) -> None:
    result = engine.resolve(
        "¿Quién ganó el mundial?",
        _unsupported_intent(),
        BusinessQuery(query_type=BusinessQueryType.UNSUPPORTED, filters={}),
        None,
    )
    assert result is not None
    assert result.fallback_type == FallbackType.OUT_OF_DOMAIN.value
    assert "Detecté una consulta relacionada con" not in result.answer


def test_top_domains_tracks_hits() -> None:
    GuidedFallbackV2Metrics.record_hit(BusinessDomain.VENTAS)
    GuidedFallbackV2Metrics.record_hit(BusinessDomain.VENTAS)
    GuidedFallbackV2Metrics.record_hit(BusinessDomain.INVENTARIO)
    top = GuidedFallbackV2Metrics.get_top_domains()
    assert top[0] == {"domain": "VENTAS", "count": 2}
    assert top[1] == {"domain": "INVENTARIO", "count": 1}
