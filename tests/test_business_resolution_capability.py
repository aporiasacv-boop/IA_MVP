from unittest.mock import MagicMock

import pytest

from app.capabilities.business_resolution_capability import BusinessResolutionCapability
from app.query_engine.business_query import BusinessQuery
from app.query_engine.query_types import BusinessQueryType
from app.query_executor.query_result import BusinessQueryResult
from app.response_engine.response_result import BusinessResponse


@pytest.fixture
def capability() -> BusinessResolutionCapability:
    query_executor = MagicMock()
    query_executor.execute.return_value = BusinessQueryResult(
        query_type="COUNT_CLIENTES",
        success=True,
        data={"total": 50},
    )
    response_engine = MagicMock()
    response_engine.generate.return_value = BusinessResponse(
        success=True,
        answer="Actualmente existen 50 clientes registrados.",
        query_type="COUNT_CLIENTES",
    )
    return BusinessResolutionCapability(query_executor, response_engine)


def test_resolve_executes_query_and_generates_response(
    capability: BusinessResolutionCapability,
) -> None:
    query = BusinessQuery(query_type=BusinessQueryType.COUNT_CLIENTES)
    stage = capability.resolve(query)

    capability._query_executor.execute.assert_called_once_with(query)
    capability._response_engine.generate.assert_called_once()
    assert stage.result.response.success is True
    assert "50 clientes" in stage.result.response.answer
    assert stage.executor_stage_ms >= 0
    assert stage.response_stage_ms >= 0


def test_resolve_preserves_query_result_as_evidence(
    capability: BusinessResolutionCapability,
) -> None:
    stage = capability.resolve(BusinessQuery(query_type=BusinessQueryType.COUNT_CLIENTES))

    assert stage.result.query_result.success is True
    assert stage.result.query_result.data["total"] == 50
