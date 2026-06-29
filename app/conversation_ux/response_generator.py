import time
from dataclasses import asdict

from app.ai_orchestration.providers.base import BaseLLMProvider
from app.conversation_ux.classifier import ConversationCategory
from app.conversation_ux.context import DatasetSnapshot
from app.conversation_ux.metrics import ConversationResponseMetrics, record_generation
from app.conversation_ux.prompt import build_conversation_response_prompt
from app.conversation_ux.schemas import ConversationGenerationContext
from app.core.settings import settings
from app.schemas.hybrid_chat import HybridChatResult


class ConversationResponseGenerator:
    """Redacta respuestas conversacionales con LLM sobre contexto ya validado."""

    def __init__(
        self,
        llm_provider: BaseLLMProvider | None = None,
        *,
        enabled: bool | None = None,
    ) -> None:
        self._llm_provider = llm_provider
        self._enabled = (
            settings.CONVERSATION_RESPONSE_LLM_ENABLED if enabled is None else enabled
        )

    def generate(self, message: str, result: HybridChatResult) -> HybridChatResult:
        if not result.metadata.get("conversation_ux_applied"):
            return result

        template_answer = result.answer
        context = self._build_context(message, result, template_answer)
        metrics = ConversationResponseMetrics()

        if not self._enabled:
            metrics.fallback_used = True
            record_generation(metrics)
            return self._with_metrics(result, template_answer, metrics)

        provider = self._resolve_provider()
        prompt = build_conversation_response_prompt(context)
        started = time.perf_counter()

        try:
            llm_result = provider.generate_response(prompt)
            rewritten = (llm_result.text or "").strip()
            if not rewritten:
                raise ValueError("Respuesta vacía del LLM")
            metrics.generation_ms = (time.perf_counter() - started) * 1000
            metrics.provider = llm_result.provider or provider.provider_name()
            metrics.model = llm_result.model or provider.model_name
            metrics.llm_applied = True
            metrics.fallback_used = False
            record_generation(metrics)
            return self._with_metrics(result, rewritten, metrics)
        except Exception:
            metrics.generation_ms = (time.perf_counter() - started) * 1000
            metrics.provider = provider.provider_name()
            metrics.model = provider.model_name
            metrics.fallback_used = True
            metrics.llm_applied = False
            record_generation(metrics)
            return self._with_metrics(result, template_answer, metrics)

    def _resolve_provider(self) -> BaseLLMProvider:
        if self._llm_provider is None:
            from app.ai_orchestration.providers.factory import create_llm_provider_with_fallback

            self._llm_provider = create_llm_provider_with_fallback()
        return self._llm_provider

    def _build_context(
        self,
        message: str,
        result: HybridChatResult,
        template_answer: str,
    ) -> ConversationGenerationContext:
        category_value = result.metadata.get("conversation_category", ConversationCategory.NONE.value)
        try:
            category = ConversationCategory(category_value)
        except ValueError:
            category = ConversationCategory.NONE

        snapshot_data = result.metadata.get("conversation_dataset_snapshot", {})
        if not isinstance(snapshot_data, dict):
            snapshot_data = {}

        capabilities = result.metadata.get("conversation_capabilities", [])
        if not isinstance(capabilities, list):
            capabilities = []

        examples = result.metadata.get("conversation_capability_examples", [])
        if not isinstance(examples, list):
            examples = []

        suggestions = (
            result.suggestions.questions
            if result.suggestions is not None
            else []
        )

        pipeline_answer = result.metadata.get("conversation_pipeline_answer", template_answer)
        if not isinstance(pipeline_answer, str):
            pipeline_answer = template_answer

        return ConversationGenerationContext(
            user_message=message,
            conversation_category=category,
            pipeline_answer=pipeline_answer,
            template_answer=template_answer,
            dataset_snapshot=snapshot_data,
            capabilities=tuple(str(item) for item in capabilities),
            capability_examples=tuple(str(item) for item in examples),
            suggested_questions=tuple(suggestions),
            pipeline_metadata={
                key: result.metadata[key]
                for key in (
                    "handled_by",
                    "query_type",
                    "fallback_type",
                    "confidence",
                    "knowledge_source",
                    "knowledge_category",
                )
                if key in result.metadata
            },
        )

    def _with_metrics(
        self,
        result: HybridChatResult,
        answer: str,
        metrics: ConversationResponseMetrics,
    ) -> HybridChatResult:
        return HybridChatResult(
            handled_by=result.handled_by,
            success=result.success,
            answer=answer,
            suggestions=result.suggestions,
            metadata={
                **result.metadata,
                **metrics.to_metadata(),
                "conversation_ux_layer": (
                    "llm_v1" if metrics.llm_applied else "presenter_v1"
                ),
            },
        )


def snapshot_to_dict(snapshot: DatasetSnapshot) -> dict:
    return {key: value for key, value in asdict(snapshot).items() if value is not None}
