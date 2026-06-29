from app.conversation_ux.classifier import ConversationCategory
from app.enterprise_personality.constants import (
    ADAPTATION_CLOSURE,
    ADAPTATION_CONSULTANT_MODE,
    ADAPTATION_DIRECT_ENGAGEMENT,
    ADAPTATION_EXPLORATION,
    ADAPTATION_GUIDED_RECOVERY,
    ADAPTATION_INSTITUTIONAL_INTRO,
)


def resolve_adaptation_type(
    category: ConversationCategory,
    *,
    conversation_turn: int = 0,
) -> str:
    if category in {ConversationCategory.GREETING, ConversationCategory.INTRODUCTION}:
        if conversation_turn <= 0:
            return ADAPTATION_INSTITUTIONAL_INTRO
        return ADAPTATION_DIRECT_ENGAGEMENT

    if category is ConversationCategory.IDENTITY:
        return (
            ADAPTATION_INSTITUTIONAL_INTRO
            if conversation_turn <= 0
            else ADAPTATION_DIRECT_ENGAGEMENT
        )

    if category is ConversationCategory.CAPABILITIES:
        return ADAPTATION_EXPLORATION

    if category is ConversationCategory.EXECUTIVE_GENERAL:
        return ADAPTATION_CONSULTANT_MODE

    if category is ConversationCategory.HELP:
        return ADAPTATION_GUIDED_RECOVERY

    if category in {ConversationCategory.FAREWELL, ConversationCategory.SOCIAL}:
        return ADAPTATION_CLOSURE

    if category in {
        ConversationCategory.CASUAL,
        ConversationCategory.SOCIAL,
    }:
        return ADAPTATION_DIRECT_ENGAGEMENT

    return ADAPTATION_DIRECT_ENGAGEMENT
