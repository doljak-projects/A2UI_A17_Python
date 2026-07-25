# A2UI Backend

Backend em Python usando **FastAPI**. Por enquanto contém apenas a estrutura base
com um endpoint de health check.

## Requisitos

- Python 3.11+

## Setup

```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env
alembic upgrade head          # cria o SQLite (a2ui.db) e as tabelas
```

## Banco de dados e migrations

SQLite em arquivo, configurado por `DATABASE_URL` (default `sqlite:///./a2ui.db`).
O schema é criado **somente por migrations** (Alembic), nunca por `create_all`:

```bash
alembic upgrade head                                # aplica as migrations pendentes
alembic revision --autogenerate -m "descrição"      # gera migration a partir dos models
alembic check                                       # acusa divergência model x migrations
alembic downgrade -1                                # desfaz a última migration
```

Todo model novo precisa ser importado em `app/models/__init__.py`, senão o
autogenerate não o enxerga.

## Executar

```bash
uvicorn app.main:app --reload --port 8000
```

- API: http://localhost:8000/api/health
- Docs (Swagger): http://localhost:8000/docs

## Testes

```bash
pytest
```

## Estrutura

```
apps/backend/
├── alembic.ini                # config do Alembic (URL vem de settings)
├── app/
│   ├── api/
│   │   ├── router.py          # agregador de rotas
│   │   └── routes/
│   │       ├── conversations.py  # CRUD /conversations
│   │       └── health.py         # endpoint /health
│   ├── core/
│   │   └── config.py          # settings (pydantic-settings)
│   ├── db/
│   │   ├── base.py            # Base declarativa (SQLAlchemy 2.0)
│   │   └── session.py         # engine, SessionLocal e dependency get_db
│   ├── models/                # models ORM
│   │   └── conversation.py
│   ├── schemas/               # schemas Pydantic
│   │   ├── conversation.py
│   │   └── health.py
│   ├── services/              # regras de negócio
│   │   └── conversation.py
│   └── main.py                # criação da app FastAPI
├── migrations/                # migrations do Alembic
│   ├── env.py
│   └── versions/
└── tests/
    ├── test_conversations.py
    └── test_health.py
```
