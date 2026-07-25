from __future__ import annotations

from collections.abc import Iterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.llm.client import HttpLLMClient
from app.llm.sse import format_sse
from app.llm.streaming import EVENT_ERROR, stream_tool_calling
from app.llm.types import Message
from app.schemas.chat import ChatRequest

router = APIRouter()

# `X-Accel-Buffering` desliga o buffer do nginx; sem isso o proxy segura os deltas
# e o cliente recebe a resposta inteira de uma vez.
SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


@router.post("/chat")
def chat(request: ChatRequest) -> StreamingResponse:
    """Responde em SSE, repassando os deltas do LLM e os eventos de tool use."""
    return StreamingResponse(
        _event_stream(request),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )


def _event_stream(request: ChatRequest) -> Iterator[str]:
    try:
        client = HttpLLMClient()
        for event in stream_tool_calling(client, _to_messages(request)):
            yield format_sse(event.type, event.data)
    except Exception as exc:
        # A resposta já começou com 200, então a falha precisa viajar como evento.
        yield format_sse(EVENT_ERROR, {"message": str(exc)})


def _to_messages(request: ChatRequest) -> list[Message]:
    return [Message(role=message.role, content=message.content) for message in request.messages]
