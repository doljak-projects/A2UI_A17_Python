from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection

import app.models  # noqa: F401  (registra os models em Base.metadata)
from alembic import context
from app.core.config import settings
from app.db.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# O SQLite não suporta a maior parte dos ALTER TABLE; o modo batch recria a
# tabela por trás dos panos e mantém as migrations portáveis.
RENDER_AS_BATCH = settings.database_url.startswith("sqlite")


def run_migrations_offline() -> None:
    """Gera o SQL das migrations sem abrir conexão (`alembic upgrade --sql`)."""
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=RENDER_AS_BATCH,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Aplica as migrations em uma conexão real.

    O engine é criado aqui (e não importado de `app.db.session`) com `NullPool`:
    o processo do Alembic é efêmero e não deve manter pool aberto.
    """
    connectable = create_engine(settings.database_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        _run_migrations(connection)


def _run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=RENDER_AS_BATCH,
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
