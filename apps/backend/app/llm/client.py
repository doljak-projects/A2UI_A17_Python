from __future__ import annotations

from typing import Any, Protocol

import httpx

from app.core.config import Settings, settings as default_settings
from app.llm.providers import (
    ANTHROPIC,
    OPENAI,
    build_messages_payload,
    build_tools_payload,
    parse_response,
)
from app.llm.types import LLMResponse, Message

ANTHROPIC_VERSION = "2023-06-01"

PROVIDER_ENDPOINTS = {
    OPENAI: "https://api.openai.com/v1/chat/completions",
    ANTHROPIC: "https://api.anthropic.com/v1/messages",
}


class LLMClient(Protocol):
    """Transporte do LLM: envia a conversa + tools e devolve a resposta normalizada."""

    provider: str

    def send(
        self, messages: list[Message], tools: list[dict[str, Any]] | None = None
    ) -> LLMResponse: ...


class HttpLLMClient:
    """Cliente HTTP (não-streaming) para OpenAI e Anthropic."""

    def __init__(
        self,
        settings: Settings | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._settings = settings or default_settings
        self.provider = self._settings.llm_provider
        self._http = http_client or httpx.Client(timeout=60.0)

    def send(
        self, messages: list[Message], tools: list[dict[str, Any]] | None = None
    ) -> LLMResponse:
        response = self._http.post(
            PROVIDER_ENDPOINTS[self.provider],
            headers=self._headers(),
            json=self._body(messages, tools),
        )
        response.raise_for_status()
        return parse_response(self.provider, response.json())

    def _headers(self) -> dict[str, str]:
        api_key = self._settings.llm_api_key.get_secret_value()
        if self.provider == ANTHROPIC:
            return {
                "x-api-key": api_key,
                "anthropic-version": ANTHROPIC_VERSION,
                "content-type": "application/json",
            }
        return {
            "Authorization": f"Bearer {api_key}",
            "content-type": "application/json",
        }

    def _body(
        self, messages: list[Message], tools: list[dict[str, Any]] | None
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "model": self._settings.llm_model,
            "temperature": self._settings.llm_temperature,
        }

        if self.provider == ANTHROPIC:
            # A Anthropic recebe o prompt de sistema fora da lista de mensagens.
            system = [m.content for m in messages if m.role == "system" and m.content]
            conversation = [m for m in messages if m.role != "system"]
            body["max_tokens"] = self._settings.llm_max_tokens
            if system:
                body["system"] = "\n".join(system)
            body["messages"] = build_messages_payload(ANTHROPIC, conversation)
        else:
            body["max_tokens"] = self._settings.llm_max_tokens
            body["messages"] = build_messages_payload(OPENAI, messages)

        if tools:
            body["tools"] = tools
            if self.provider == OPENAI:
                body["tool_choice"] = "auto"

        return body


def build_tools_for_client(client: LLMClient, tools_schema: list[dict[str, Any]]):
    """Atalho para montar o payload de tools no formato do provedor do cliente."""
    return build_tools_payload(client.provider, tools_schema)
