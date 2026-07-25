from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

TITLE_MAX_LENGTH = 200


class ConversationCreate(BaseModel):
    """Payload de criação. Espaços nas pontas são removidos antes de validar,
    então um título só de espaços é rejeitado como vazio."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=TITLE_MAX_LENGTH)


class ConversationUpdate(BaseModel):
    """Payload de update parcial: campos ausentes (ou nulos) são ignorados."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=TITLE_MAX_LENGTH)


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    created_at: datetime
    updated_at: datetime
