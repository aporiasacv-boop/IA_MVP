from app.capability_discovery.v2.constants import EXAMPLES_LINE, INTRO_LINE


def build_v2_answer(
    capabilities: tuple[str, ...] | list[str],
    examples: tuple[str, ...] | list[str],
) -> str:
    lines = [INTRO_LINE, ""]
    lines.extend(f"• {capability}" for capability in capabilities)
    lines.extend(["", EXAMPLES_LINE])
    lines.extend(f"• {question}" for question in examples)
    return "\n".join(lines)
