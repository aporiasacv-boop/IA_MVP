import pytest

from app.conversation_ux.classifier import ConversationCategory, classify_message, greeting_time_phrase


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("Hola", ConversationCategory.GREETING),
        ("Adiós", ConversationCategory.FAREWELL),
        ("Buenos días", ConversationCategory.GREETING),
        ("¿Cómo estás?", ConversationCategory.CASUAL),
        ("Gracias", ConversationCategory.SOCIAL),
        ("Preséntate", ConversationCategory.INTRODUCTION),
        ("¿Quién eres?", ConversationCategory.IDENTITY),
        ("¿Qué puedes hacer?", ConversationCategory.CAPABILITIES),
        ("¿Cómo ves el negocio?", ConversationCategory.EXECUTIVE_GENERAL),
        ("¿Qué información tienes?", ConversationCategory.EXECUTIVE_GENERAL),
        ("Ayuda", ConversationCategory.HELP),
        ("¿Cuántos clientes existen?", ConversationCategory.NONE),
        ("Resumen de junio", ConversationCategory.NONE),
    ],
)
def test_classify_message(message: str, expected: ConversationCategory) -> None:
    assert classify_message(message) is expected


def test_greeting_time_phrase_morning() -> None:
    assert greeting_time_phrase("Buenos días") == "Buenos días"


def test_greeting_time_phrase_default() -> None:
    assert greeting_time_phrase("Hola") == "Hola"
