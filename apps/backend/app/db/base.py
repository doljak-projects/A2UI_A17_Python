from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarativa única do projeto.

    Todo model precisa herdar daqui para entrar em `Base.metadata`, que é o
    `target_metadata` usado pelo Alembic no autogenerate.
    """
