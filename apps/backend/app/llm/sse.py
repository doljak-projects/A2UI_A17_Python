from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from typing import Any

DATA_PREFIX = "data:"
DONE_SENTINEL = "[DONE]"


def iter_sse_json(lines: Iterable[str]) -> Iterator[dict[str, Any]]:
    """Extrai os payloads JSON das linhas `data:` de um stream SSE.

    Serve tanto para a OpenAI quanto para a Anthropic: linhas `event:`, comentários
    e linhas em branco são ignorados, e o sentinela `[DONE]` encerra o stream.
    """
    for line in lines:
        if not line.startswith(DATA_PREFIX):
            continue

        payload = line[len(DATA_PREFIX) :].strip()
        if not payload:
            continue
        if payload == DONE_SENTINEL:
            return

        yield json.loads(payload)


def format_sse(event: str, data: dict[str, Any]) -> str:
    """Serializa um evento no formato SSE (`event:` + `data:` + linha em branco)."""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
