"""Decide cidade e tipo de card a partir da última mensagem do usuário."""

from __future__ import annotations

import re
from typing import Any, Literal

CardKind = Literal["weather", "humidity"]

DEFAULT_CITY = "São Paulo"
CORDIAL_REPLY = "Opa, é pra já!"

HUMIDITY_HINTS = ("umidade", "humidity", "úmido", "umido")
_WEATHER_INTENT = re.compile(
    r"""
    \b(
        clima|temperatura|umidade|humidity|weather|forecast|
        graus|chuva|chove|nublado|ensolarado|calor|tempo
    )\b
    |°\s*c
    """,
    re.IGNORECASE | re.VERBOSE,
)

_FILLER = re.compile(
    r"""
    \b(
        qual|quais|como|esta|está|estão|estao|o|a|os|as|um|uma|
        em|no|na|nos|nas|pra|para|por|favor|
        me|mostra|mostre|fala|fale|diz|diga|veja|ver|
        hoje|agora|atual|clima|tempo|temperatura|umidade|
        humidity|weather|graus?
    )\b
    """,
    re.IGNORECASE | re.VERBOSE,
)
_PUNCT = re.compile(r"[?!.,;:]+")
_SPACES = re.compile(r"\s+")
_PARTICLES = {"de", "do", "da", "dos", "das", "e"}


def message_text(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("text"):
                parts.append(str(item["text"]))
            else:
                text = getattr(item, "text", None)
                if text:
                    parts.append(str(text))
        return " ".join(parts).strip()
    return ""


def last_user_text(messages: list[Any]) -> str:
    for message in reversed(messages):
        if getattr(message, "role", None) != "user":
            continue
        text = message_text(getattr(message, "content", ""))
        if text:
            return text
    return ""


def has_weather_intent(text: str) -> bool:
    """Só é clima/umidade se a pergunta pedir isso — cidade sozinha não conta."""
    return bool(text and _WEATHER_INTENT.search(text))


def resolve_card_kind(text: str) -> CardKind:
    lowered = text.casefold()
    if any(hint in lowered for hint in HUMIDITY_HINTS):
        return "humidity"
    return "weather"


def resolve_city(text: str, default: str = DEFAULT_CITY) -> str:
    cleaned = _PUNCT.sub(" ", text)
    cleaned = _FILLER.sub(" ", cleaned)
    cleaned = _SPACES.sub(" ", cleaned).strip()
    if not cleaned:
        return default
    return _title_city(cleaned)


def _title_city(text: str) -> str:
    words = text.split()
    titled: list[str] = []
    for index, word in enumerate(words):
        lower = word.casefold()
        if index > 0 and lower in _PARTICLES:
            titled.append(lower)
        else:
            titled.append(word[:1].upper() + word[1:].lower() if word else word)
    return " ".join(titled)
