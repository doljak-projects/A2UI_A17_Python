from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


def _connect_args(database_url: str) -> dict[str, object]:
    """O SQLite do CPython recusa conexões usadas fora da thread que as criou.

    O FastAPI atende rotas `def` em threads do pool, então a checagem precisa ser
    desligada; para outros bancos não há argumento extra.
    """
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


engine: Engine = create_engine(
    settings.database_url,
    connect_args=_connect_args(settings.database_url),
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """Dependency do FastAPI: uma sessão por request, sempre fechada no fim."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
