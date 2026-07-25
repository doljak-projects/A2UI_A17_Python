from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Mensagem da conversa enviada pelo cliente."""

    role: Literal["system", "user", "assistant"] = "user"
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    """Histórico completo da conversa; o backend não mantém estado entre chamadas."""

    messages: list[ChatMessage] = Field(min_length=1)
