from app.core.settings import settings

LLM_ROUTES = frozenset({"legacy_chat", "executive_reasoning"})
KNOWLEDGE_ROUTES = frozenset({"product_identity", "business_knowledge"})
PIPELINE_ROUTES = frozenset({"business_pipeline"})

PROVIDER_INPUT_RATES = {
    "openai": settings.GPT_COST_PER_1K_INPUT_TOKENS,
    "gpt": settings.GPT_COST_PER_1K_INPUT_TOKENS,
    "claude": settings.CLAUDE_COST_PER_1K_INPUT_TOKENS,
    "anthropic": settings.CLAUDE_COST_PER_1K_INPUT_TOKENS,
    "ollama": settings.OLLAMA_COST_PER_1K_TOKENS,
    "mock": 0.0,
}

PROVIDER_OUTPUT_RATES = {
    "openai": settings.GPT_COST_PER_1K_OUTPUT_TOKENS,
    "gpt": settings.GPT_COST_PER_1K_OUTPUT_TOKENS,
    "claude": settings.CLAUDE_COST_PER_1K_OUTPUT_TOKENS,
    "anthropic": settings.CLAUDE_COST_PER_1K_OUTPUT_TOKENS,
    "ollama": settings.OLLAMA_COST_PER_1K_TOKENS,
    "mock": 0.0,
}


def usd_to_mxn(amount_usd: float) -> float:
    return round(amount_usd * settings.USD_TO_MXN_RATE, 4)


def estimate_tokens_from_text(text: str) -> int:
    return max(len(text) // 4, 0)


def provider_token_cost_usd(provider: str, input_tokens: int, output_tokens: int) -> float:
    key = provider.lower()
    input_rate = PROVIDER_INPUT_RATES.get(key, settings.GPT_COST_PER_1K_INPUT_TOKENS)
    output_rate = PROVIDER_OUTPUT_RATES.get(key, settings.GPT_COST_PER_1K_OUTPUT_TOKENS)
    return round(
        (input_tokens / 1000.0) * input_rate + (output_tokens / 1000.0) * output_rate,
        6,
    )


def benchmark_cost_usd(provider: str, input_tokens: int, output_tokens: int) -> float:
    return provider_token_cost_usd(provider, input_tokens, output_tokens)


def avoided_llm_cost_usd(
    *,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    benchmark_provider: str = "openai",
) -> float:
    tokens_in = input_tokens if input_tokens is not None else int(settings.FINOPS_BASELINE_INPUT_TOKENS)
    tokens_out = output_tokens if output_tokens is not None else int(settings.FINOPS_BASELINE_OUTPUT_TOKENS)
    return benchmark_cost_usd(benchmark_provider, tokens_in, tokens_out)


def is_llm_route(handled_by: str) -> bool:
    return handled_by in LLM_ROUTES


def is_knowledge_route(handled_by: str) -> bool:
    return handled_by in KNOWLEDGE_ROUTES


def is_pipeline_route(handled_by: str) -> bool:
    return handled_by in PIPELINE_ROUTES
