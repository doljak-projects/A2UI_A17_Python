# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Visão geral

A2UI é um monorepo com dois apps independentes sob `apps/`:

- `apps/frontend` — Angular 17 (standalone) + Angular Material, gerenciado como npm workspace da raiz.
- `apps/backend` — Python 3.11+ / FastAPI, **fora** dos npm workspaces (é gerenciado por pip/venv). Os scripts `be:*` na raiz apenas fazem `cd apps/backend`.

O projeto está em estágio inicial: frontend com app shell (toolbar Material, tema `azure-blue`, página `home`) e backend com o endpoint `GET /api/health`.

## Comandos

Da raiz (atalhos de conveniência definidos no `package.json`):

```bash
npm install          # instala deps do workspace frontend
npm run fe:start     # ng serve  -> http://localhost:4200
npm run fe:build     # build de produção do frontend
npm run fe:test      # testes unitários (Karma/Jasmine)
npm run be:start     # uvicorn app.main:app --reload --port 8000
npm run be:test      # pytest (do diretório apps/backend)
```

Backend — setup e uso (o venv é obrigatório; o backend não está nos workspaces npm):

```bash
cd apps/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000   # docs em /docs, redoc em /redoc
pytest                    # roda toda a suíte
pytest tests/test_health.py::test_health   # roda um único teste
ruff check .              # lint (ruff configurado no pyproject.toml, line-length 100)
```

Frontend — comandos diretos (de `apps/frontend`, ou via `npm --workspace apps/frontend run <script>`):

```bash
ng test --include='**/app.component.spec.ts'   # roda um único arquivo de spec
ng build --watch --configuration development    # build incremental
```

## Arquitetura

### Backend (FastAPI)

O app é montado por uma **factory** `create_app()` em `app/main.py`, que aplica CORS e inclui `api_router` com o prefixo `settings.api_prefix` (`/api`). Ao adicionar rotas, siga a cadeia de inclusão de routers:

- `app/api/routes/<recurso>.py` — define um `APIRouter` com os endpoints do recurso.
- `app/api/router.py` — agrega os routers de recursos em `api_router` (com `tags`).
- Schemas de request/response ficam em `app/schemas/` (Pydantic); os endpoints declaram `response_model`.

Configuração é centralizada em `app/core/config.py` via `pydantic-settings`: a classe `Settings` lê do `.env`, e a instância única é exposta como `settings` (cacheada com `@lru_cache` em `get_settings()`). Sempre importe `settings` daqui em vez de ler env vars diretamente. `CORS_ORIGINS` é uma lista JSON no `.env`.

Diretórios `app/models/` e `app/services/` existem como estrutura base (ainda vazios) para camada de dados e lógica de negócio.

### Frontend (Angular 17 standalone)

Não há `NgModule` — a aplicação usa a API standalone:

- Bootstrap em `src/main.ts` via `bootstrapApplication(AppComponent, appConfig)`.
- Providers globais em `src/app/app.config.ts` (`provideRouter`, `provideAnimationsAsync`). Adicione providers de app aqui.
- Rotas em `src/app/app.routes.ts`; páginas ficam em `src/app/pages/<nome>/`.
- Componentes são `standalone: true` e importam seus próprios módulos Material no array `imports`. Estilo padrão é SCSS (configurado no schematic do `angular.json`).

## Git workflow (regra do projeto)

O usuário faz **branches, commits e pull requests manualmente**. NÃO criar branches, NÃO fazer `git commit`/`git add` para commitar, NÃO abrir/gerenciar PRs. Comandos de leitura (`git status`, `git diff`, `git log`) são permitidos. Deixe as alterações no working tree para o usuário revisar. Só execute ações git de escrita se o usuário pedir explicitamente naquele momento.
