from app.schemas.prompt_metrics import PromptMetrics, PromptAuditResult


class PromptAudit:
    TOKEN_CHAR_RATIO = 4

    @classmethod
    def analyze(
        cls,
        question: str,
        prompt: str,
        context_chars: int,
        sources_used: list[str] | None = None,
        answer: str = "",
    ) -> PromptAuditResult:
        question_chars = len(question.strip())
        prompt_chars = len(prompt)
        response_chars = len(answer)
        estimated_tokens = max(1, prompt_chars // cls.TOKEN_CHAR_RATIO)
        metrics = PromptMetrics(
            prompt_chars=prompt_chars,
            context_chars=context_chars,
            question_chars=question_chars,
            response_chars=response_chars,
            estimated_tokens=estimated_tokens,
            sources_used=sources_used or [],
        )
        preview = prompt[:500] + ("..." if len(prompt) > 500 else "")
        return PromptAuditResult(metrics=metrics, prompt_preview=preview)

    @classmethod
    def estimate_tokens(cls, text: str) -> int:
        return max(1, len(text) // cls.TOKEN_CHAR_RATIO)
