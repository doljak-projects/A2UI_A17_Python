from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

from app.llm.client import StreamingLLMClient, build_tools_for_client
from app.llm.providers import ANTHROPIC, OPENAI, UnsupportedProviderError
from app.llm.tool_calling import (
    DEFAULT_MAX_ROUNDS,
    MaxToolRoundsExceededError,
    execute_tool_calls,
)
from app.llm.types import LLMResponse, Message, ToolCall
from app.tools.registry import ToolRegistry, registry as default_registry

EVENT_DELTA = "delta"
EVENT_TOOL_CALL = "tool_call"
EVENT_TOOL_RESULT = "tool_result"
EVENT_DONE = "done"
EVENT_ERROR = "error"


@dataclass(frozen=True)
class StreamEvent:
    """Evento do loop de chat, agnóstico de transporte (o SSE é montado na API)."""

    type: str
    data: dict[str, Any]


@dataclass
class _ToolCallDraft:
    """Tool call em construção, remontada a partir dos fragmentos do stream."""

    id: str = ""
    name: str = ""
    arguments: list[str] = field(default_factory=list)

    def to_tool_call(self) -> ToolCall:
        return ToolCall(id=self.id, name=self.name, arguments=_loads("".join(self.arguments)))


class OpenAIStreamAccumulator:
    """Junta os deltas da OpenAI até formar a resposta completa da rodada."""

    def __init__(self) -> None:
        self._texts: list[str] = []
        self._drafts: dict[int, _ToolCallDraft] = {}
        self._stop_reason: str | None = None

    def feed(self, chunk: dict[str, Any]) -> Iterator[str]:
        choice = (chunk.get("choices") or [{}])[0]
        delta = choice.get("delta") or {}

        if choice.get("finish_reason"):
            self._stop_reason = choice["finish_reason"]

        for call in delta.get("tool_calls") or []:
            draft = self._drafts.setdefault(call.get("index", 0), _ToolCallDraft())
            if call.get("id"):
                draft.id = call["id"]
            function = call.get("function") or {}
            if function.get("name"):
                draft.name = function["name"]
            if function.get("arguments"):
                draft.arguments.append(function["arguments"])

        text = delta.get("content")
        if text:
            self._texts.append(text)
            yield text

    def result(self) -> LLMResponse:
        return _build_response(self._texts, self._drafts, self._stop_reason)


class AnthropicStreamAccumulator:
    """Junta os eventos de content block da Anthropic até formar a resposta."""

    def __init__(self) -> None:
        self._texts: list[str] = []
        self._drafts: dict[int, _ToolCallDraft] = {}
        self._stop_reason: str | None = None

    def feed(self, chunk: dict[str, Any]) -> Iterator[str]:
        chunk_type = chunk.get("type")
        index = chunk.get("index", 0)

        if chunk_type == "content_block_start":
            block = chunk.get("content_block") or {}
            if block.get("type") == "tool_use":
                self._drafts[index] = _ToolCallDraft(
                    id=block.get("id", ""), name=block.get("name", "")
                )

        elif chunk_type == "content_block_delta":
            delta = chunk.get("delta") or {}
            if delta.get("type") == "text_delta" and delta.get("text"):
                self._texts.append(delta["text"])
                yield delta["text"]
            elif delta.get("type") == "input_json_delta" and index in self._drafts:
                self._drafts[index].arguments.append(delta.get("partial_json", ""))

        elif chunk_type == "message_delta":
            stop_reason = (chunk.get("delta") or {}).get("stop_reason")
            if stop_reason:
                self._stop_reason = stop_reason

    def result(self) -> LLMResponse:
        return _build_response(self._texts, self._drafts, self._stop_reason)


StreamAccumulator = OpenAIStreamAccumulator | AnthropicStreamAccumulator

ACCUMULATORS = {
    OPENAI: OpenAIStreamAccumulator,
    ANTHROPIC: AnthropicStreamAccumulator,
}


def make_accumulator(provider: str) -> StreamAccumulator:
    try:
        return ACCUMULATORS[provider]()
    except KeyError as exc:
        raise UnsupportedProviderError(f"Provedor '{provider}' não suportado") from exc


def stream_tool_calling(
    client: StreamingLLMClient,
    messages: list[Message],
    registry: ToolRegistry | None = None,
    max_rounds: int = DEFAULT_MAX_ROUNDS,
) -> Iterator[StreamEvent]:
    """Versão em streaming de `run_tool_calling`, emitindo eventos conforme chegam.

    Cada rodada abre um request novo ao provedor, mas o consumidor enxerga um único
    fluxo contínuo de eventos: deltas de texto, tools pedidas e seus resultados.
    """
    registry = registry or default_registry
    tools = build_tools_for_client(client, registry.get_tools_schema())
    conversation = list(messages)

    for round_number in range(1, max_rounds + 1):
        accumulator = make_accumulator(client.provider)

        for chunk in client.stream(conversation, tools):
            for text in accumulator.feed(chunk):
                yield StreamEvent(EVENT_DELTA, {"text": text})

        response = accumulator.result()

        if not response.requires_tool_execution:
            yield StreamEvent(EVENT_DONE, {"text": response.text or "", "rounds": round_number})
            return

        conversation.append(
            Message(
                role="assistant",
                content=response.text,
                tool_calls=response.tool_calls,
            )
        )

        for call in response.tool_calls:
            yield StreamEvent(
                EVENT_TOOL_CALL,
                {"id": call.id, "name": call.name, "arguments": call.arguments},
            )

        results = execute_tool_calls(response.tool_calls, registry)
        for result in results:
            yield StreamEvent(
                EVENT_TOOL_RESULT,
                {
                    "id": result.tool_call_id,
                    "name": result.name,
                    "content": result.content,
                    "is_error": result.is_error,
                },
            )

        conversation.append(Message(role="tool", tool_results=results))

    raise MaxToolRoundsExceededError(
        f"LLM excedeu o limite de {max_rounds} rodadas de tool calling"
    )


def _build_response(
    texts: list[str], drafts: dict[int, _ToolCallDraft], stop_reason: str | None
) -> LLMResponse:
    return LLMResponse(
        text="".join(texts) or None,
        tool_calls=[draft.to_tool_call() for _, draft in sorted(drafts.items())],
        stop_reason=stop_reason,
    )


def _loads(raw: str) -> dict[str, Any]:
    return json.loads(raw) if raw else {}
