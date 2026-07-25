from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.conversation import Conversation
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
)
from app.services import conversation as conversation_service
from app.services.conversation import (
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    ConversationNotFoundError,
)

router = APIRouter(prefix="/conversations")

DbSession = Annotated[Session, Depends(get_db)]


def _not_found(exc: ConversationNotFoundError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(payload: ConversationCreate, db: DbSession) -> Conversation:
    return conversation_service.create(db, payload)


@router.get("", response_model=list[ConversationResponse])
def list_conversations(
    db: DbSession,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
) -> list[Conversation]:
    return list(conversation_service.list(db, skip=skip, limit=limit))


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: int, db: DbSession) -> Conversation:
    try:
        return conversation_service.get(db, conversation_id)
    except ConversationNotFoundError as exc:
        raise _not_found(exc) from exc


@router.patch("/{conversation_id}", response_model=ConversationResponse)
def update_conversation(
    conversation_id: int, payload: ConversationUpdate, db: DbSession
) -> Conversation:
    try:
        return conversation_service.update(db, conversation_id, payload)
    except ConversationNotFoundError as exc:
        raise _not_found(exc) from exc


# `response_model=None` é obrigatório: sem isso o FastAPI deriva um response model
# do `-> None` e recusa a rota, porque 204 não pode ter corpo.
@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
def delete_conversation(conversation_id: int, db: DbSession) -> None:
    try:
        conversation_service.delete(db, conversation_id)
    except ConversationNotFoundError as exc:
        raise _not_found(exc) from exc
