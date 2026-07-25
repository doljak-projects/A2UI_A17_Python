"""Models ORM.

Todo model precisa ser importado aqui para que `Base.metadata` esteja completo
quando o Alembic gerar/aplicar migrations.
"""

from app.models.conversation import Conversation

__all__ = ["Conversation"]
