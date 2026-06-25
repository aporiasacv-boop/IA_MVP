import uuid
from datetime import datetime, timezone

from app.operational_metrics.cost_engine import (
    avoided_llm_cost_usd,
    estimate_tokens_from_text,
    is_knowledge_route,
    is_llm_route,
    is_pipeline_route,
    provider_token_cost_usd,
    usd_to_mxn,
)
from app.operational_metrics.schemas import OperationalQueryRecord
from app.schemas.hybrid_chat import HybridChatRequest, HybridChatResult


def build_operational_record(
    *,
    request: HybridChatRequest,
    result: HybridChatResult,
    wall_time_ms: float,
    user_id: str | None = None,
    channel: str = "hybrid",
) -> OperationalQueryRecord:
    metadata = result.metadata or {}
    handled_by = result.handled_by
    query_type = (
        metadata.get("query_type")
        or metadata.get("fallback_type")
        or metadata.get("pending_query_type")
    )
    intent = metadata.get("intent")
    verb = metadata.get("verb")
    confidence = float(metadata.get("confidence", 0.0) or 0.0)
    response_time_ms = float(metadata.get("response_time_ms", wall_time_ms) or wall_time_ms)

    input_tokens = int(metadata.get("tokens_input", 0) or 0)
    output_tokens = int(metadata.get("tokens_output", 0) or 0)
    token_source = "none"
    estimated_tokens = 0

    llm_used = is_llm_route(handled_by)
    llm_provider = metadata.get("provider") or metadata.get("llm_provider")
    llm_model = metadata.get("model") or metadata.get("llm_model")

    if handled_by == "executive_reasoning" and (input_tokens or output_tokens):
        token_source = "api"
    elif handled_by == "legacy_chat":
        estimated_tokens = estimate_tokens_from_text(request.message) + estimate_tokens_from_text(result.answer)
        if input_tokens == 0 and output_tokens == 0:
            input_tokens = estimate_tokens_from_text(request.message)
            output_tokens = estimate_tokens_from_text(result.answer)
            token_source = "estimated"
        else:
            token_source = "api" if (input_tokens or output_tokens) else "estimated"
        llm_provider = llm_provider or "ollama"
        llm_model = llm_model or "qwen3:8b"
    elif llm_used:
        token_source = "estimated"
        estimated_tokens = estimate_tokens_from_text(request.message) + estimate_tokens_from_text(result.answer)
        input_tokens = input_tokens or estimate_tokens_from_text(request.message)
        output_tokens = output_tokens or estimate_tokens_from_text(result.answer)

    total_tokens = input_tokens + output_tokens
    if estimated_tokens == 0 and total_tokens > 0:
        estimated_tokens = total_tokens

    cost_usd = 0.0
    if handled_by == "executive_reasoning" and metadata.get("estimated_cost") is not None:
        cost_usd = float(metadata.get("estimated_cost", 0.0) or 0.0)
        if llm_provider:
            token_source = "api" if (input_tokens or output_tokens) else "estimated"
    elif llm_used and llm_provider:
        cost_usd = provider_token_cost_usd(str(llm_provider), input_tokens, output_tokens)
    elif llm_used:
        cost_usd = provider_token_cost_usd("openai", input_tokens, output_tokens)

    avoided_cost_usd = 0.0
    if not llm_used:
        avoided_cost_usd = avoided_llm_cost_usd(
            input_tokens=input_tokens or estimate_tokens_from_text(request.message),
            output_tokens=output_tokens or estimate_tokens_from_text(result.answer),
        )

    provider = str(llm_provider or handled_by)
    model = str(llm_model or query_type or "")

    return OperationalQueryRecord(
        request_id=uuid.uuid4().hex,
        timestamp=datetime.now(timezone.utc),
        session_id=request.session_id,
        handled_by=handled_by,
        provider=provider,
        model=model,
        user_id=user_id,
        channel=channel,
        query_type=str(query_type) if query_type else None,
        verb=str(verb) if verb else None,
        intent=str(intent) if intent else None,
        response_time_ms=round(response_time_ms, 2),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        estimated_tokens=estimated_tokens,
        token_source=token_source,
        cache_hit=bool(metadata.get("cache_hit", False)),
        knowledge_hit=is_knowledge_route(handled_by),
        pipeline_hit=is_pipeline_route(handled_by),
        executive_reasoning=handled_by == "executive_reasoning",
        llm_used=llm_used,
        llm_provider=str(llm_provider) if llm_provider else None,
        llm_model=str(llm_model) if llm_model else None,
        success=result.success,
        confidence=confidence,
        cost_usd=round(cost_usd, 6),
        cost_mxn=usd_to_mxn(cost_usd),
        avoided_cost_usd=round(avoided_cost_usd, 6),
    )
