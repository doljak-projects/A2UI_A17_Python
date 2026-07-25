---
issue: 8
title: "BE: Implementar CRUD end-to-end de entidade de exemplo"
branch: feat/8-crud-conversation-crud-end-to-end
status: closed
last_updated: 07-25-2026
---

# Issue #8 — CRUD end-to-end da entidade Conversation

## Status
Feita — CRUD de `Conversation` com camada de banco, migration Alembic versionada e 20 testes de integração.

## O que foi feito
- `app/db/base.py` e `app/db/session.py`: nova camada de banco. `Base(DeclarativeBase)` é a única base declarativa (é o `target_metadata` do Alembic) e `session.py` expõe engine, `SessionLocal` e a dependency `get_db()` (uma sessão por request, sempre fechada). `check_same_thread=False` é aplicado só quando a URL é SQLite, e `expire_on_commit=False` evita um SELECT extra ao serializar o objeto depois do commit.
- `app/core/config.py` + `.env.example`: `database_url` (default `sqlite:///./a2ui.db`) em seção própria. É a única fonte da URL — a app e o Alembic leem daqui.
- `app/models/conversation.py`: model no estilo SQLAlchemy 2.0 (`Mapped`/`mapped_column`). `created_at`/`updated_at` usam `server_default=func.now()` e `onupdate=func.now()`, ou seja, o timestamp é responsabilidade do banco e não da app — inserts feitos fora da API também ficam consistentes. `app/models/__init__.py` importa o model para completar `Base.metadata`.
- `app/schemas/conversation.py`: `ConversationCreate` (título obrigatório, 1–200 chars), `ConversationUpdate` (título opcional, para PATCH parcial) e `ConversationResponse` com `from_attributes=True`. `str_strip_whitespace=True` faz um título só de espaços virar `""` e cair no 422.
- `app/services/conversation.py`: `create`/`get`/`list`/`update`/`delete` recebendo `Session`. O service não conhece HTTP: quando o registro não existe levanta `ConversationNotFoundError` (subclasse de `LookupError`, carrega o `conversation_id`).
- `app/api/routes/conversations.py`: `POST` (201), `GET` lista com `skip`/`limit` validados, `GET/{id}`, `PATCH/{id}` (parcial) e `DELETE/{id}` (204). A tradução `ConversationNotFoundError` → `HTTPException(404)` acontece só aqui, via helper `_not_found`. Registrado em `app/api/router.py` com `tags=["conversations"]`.
- `alembic.ini` + `migrations/`: Alembic inicializado dentro de `apps/backend`. O `env.py` lê `settings.database_url` (a chave `sqlalchemy.url` do ini foi removida de propósito) e cria o próprio engine com `NullPool`, já que o processo é efêmero. Migration inicial `a29dbfee5c28_create_conversations_table.py` versionada.
- `requirements.txt`: `sqlalchemy>=2.0,<2.1` e `alembic>=1.14,<1.15`.
- `apps/backend/.gitignore`: `*.db`, `*.db-journal` e `*.sqlite3` (o `.gitignore` da raiz não cobria arquivos de banco).
- `tests/test_conversations.py`: 20 testes de integração com `TestClient` e SQLite descartável em `tmp_path`, trocando `get_db` por `app.dependency_overrides`.
- `apps/backend/README.md`: seção de banco/migrations e árvore de diretórios atualizada.
- `package.json` da raiz: scripts `be:migrate` e `be:migration`, seguindo a convenção `be:*`/`fe:*` já existente no monorepo.

## Como rastrear
- Branch: `feat/8-crud-conversation-crud-end-to-end`
- Worktree: `8-worktree-crud`
- Arquivos principais: `apps/backend/app/db/session.py`, `apps/backend/app/models/conversation.py`, `apps/backend/app/schemas/conversation.py`, `apps/backend/app/services/conversation.py`, `apps/backend/app/api/routes/conversations.py`, `apps/backend/migrations/versions/a29dbfee5c28_create_conversations_table.py`, `apps/backend/tests/test_conversations.py`

## Notes
- **Ordenação da listagem é por `id`, não por `created_at`**: o `CURRENT_TIMESTAMP` do SQLite tem precisão de segundos, então registros criados na mesma chamada empatariam e a paginação deixaria de ser estável.
- **Timestamps voltam em UTC e sem timezone**: `DateTime(timezone=True)` foi mantido pensando em Postgres, mas o SQLite não guarda offset — a resposta é naive (ex.: `2026-07-25T16:50:51` para 13:50 local). Se o frontend precisar de fuso, resolver antes de expor a data.
- **`DELETE` precisa de `response_model=None` explícito**: com só `-> None`, o FastAPI deriva um response model e recusa a rota, porque 204 não pode ter corpo.
- **PATCH com `{"title": null}` é tratado como "não informado"** (o service usa `exclude_unset=True, exclude_none=True`), em vez de 422. Foi a escolha mais segura contra violar o `NOT NULL`, mas é um comportamento silencioso — vale revisar se o padrão desejado é rejeitar o `null` explícito.
- `render_as_batch` fica ligado quando a URL é SQLite: sem isso, migrations futuras com `ALTER TABLE` (drop/alter de coluna) quebram no SQLite.
- Os testes criam as tabelas com `create_all` por velocidade; o `alembic upgrade head` é validado separadamente. Isso significa que uma divergência entre model e migration não apareceria na suíte — use `alembic check` (rodado e limpo) como rede de segurança.
- O `env.py` importa `app.core.config`, que exige `LLM_API_KEY`/`LLM_MODEL`. Consequência prática: sem `.env` configurado, `alembic` falha na validação dos settings, igual à app.
- Validação: 60 testes passando (40 pré-existentes + 20 novos), `ruff check` limpo, `alembic upgrade head` / `downgrade base` / `upgrade head` num banco limpo criando a tabela `conversations`, `alembic check` sem divergências, e smoke test manual com uvicorn na porta 8132 cobrindo os 5 endpoints (201, 200, 404, 204, 422).
