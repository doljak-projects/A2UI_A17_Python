from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.schemas.conversation import ConversationCreate, ConversationUpdate

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100


class ConversationNotFoundError(LookupError):
    """Levantada quando a conversa referenciada não existe.

    É um erro de domínio: a tradução para HTTP 404 é responsabilidade do router.
    """

    def __init__(self, conversation_id: int) -> None:
        super().__init__(f"Conversa {conversation_id} não encontrada")
        self.conversation_id = conversation_id


def create(db: Session, data: ConversationCreate) -> Conversation:
    """Cria a conversa e devolve o registro já com os timestamps do banco."""
    conversation = Conversation(title=data.title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get(db: Session, conversation_id: int) -> Conversation:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise ConversationNotFoundError(conversation_id)
    return conversation


def list(db: Session, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE) -> Sequence[Conversation]:
    """Lista paginada, ordenada por `id`.

    A ordenação é por `id` e não por `created_at` porque o SQLite grava o
    timestamp com precisão de segundos: registros criados juntos empatariam e a
    paginação deixaria de ser estável.
    """
    statement = select(Conversation).order_by(Conversation.id).offset(skip).limit(limit)
    return db.execute(statement).scalars().all()


def update(db: Session, conversation_id: int, data: ConversationUpdate) -> Conversation:
    """Aplica um update parcial; sem campos informados, nada é alterado."""
    conversation = get(db, conversation_id)

    changes = data.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in changes.items():
        setattr(conversation, field, value)

    db.commit()
    db.refresh(conversation)
    return conversation


def delete(db: Session, conversation_id: int) -> None:
    conversation = get(db, conversation_id)
    db.delete(conversation)
    db.commit()
