# A2UI — POC Agêntica com AG-UI + Angular 17

POC de estudo explorando o uso combinado de **A2UI** (design system Angular Material) e **AG-UI Protocol** para construção de uma interface Angular verdadeiramente agêntica, onde componentes de UI são renderizados dinamicamente a partir de um catálogo JSON dirigido por um LLM via streaming.

O fluxo central é: usuário interage via chat → LLM escolhe tools (WeatherAPI, CRUD, etc.) → backend emite eventos AG-UI → frontend renderiza componentes A2UI reativamente via **Angular Signals**.

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | Angular 17 (standalone + Signals) + Angular Material |
| Backend | Python 3.11 / FastAPI |
| Protocolo agêntico | AG-UI (client + server) |
| LLM | Configurável via `.env` (OpenAI / Anthropic) |
| API externa | OpenWeatherMap (via tool call) |
| MCP | Tools expostas via MCP server no backend |

## Estrutura

```
a2ui/
├── apps/
│   ├── frontend/   # Angular 17 + Angular Material (Design System)
│   └── backend/    # Python + FastAPI (estrutura base)
├── package.json    # workspace raiz + scripts de conveniência
├── .editorconfig
└── .gitignore
```

## Requisitos

- Node.js 18+ e npm
- Python 3.11+

## Rodar localmente (frontend + backend)

```bash
./dev.sh
```

Sobe os dois serviços em paralelo e encerra ambos com `Ctrl+C`.
Pré-requisitos: venv criado em `apps/backend/.venv` e `.env` preenchido (veja abaixo).

| Serviço | URL |
|---|---|
| Frontend | http://localhost:4200 |
| Backend (Swagger) | http://localhost:8000/docs |
| MCP Server | http://localhost:8000/mcp |

## Frontend (Angular 17 + Material)

```bash
npm install                 # instala deps do workspace frontend
npm run fe:start            # ng serve  -> http://localhost:4200
npm run fe:build            # build de produção
npm run fe:test             # testes unitários (Karma/Jasmine)
```

## Backend (Python / FastAPI)

```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000   # http://localhost:8000/docs
```

Ou pela raiz:

```bash
npm run be:start
npm run be:test
```

### MCP Server

A mesma app FastAPI expõe as tools do backend via **MCP** (Streamable HTTP) em
`http://127.0.0.1:8000/mcp`. Para apontar o Cursor para ele, em `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "a2ui-backend": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

Configuração do Claude Desktop, teste rápido com um cliente Python e detalhes de
implementação estão em [`docs/mcp.md`](docs/mcp.md).

> Documentação completa do backend (endpoints, variáveis de ambiente, banco de dados, estrutura): [`apps/backend/README.md`](apps/backend/README.md)

---

## Workflow de Desenvolvimento

Cada issue tem uma branch e uma worktree dedicada, criadas via `/doljak-create-issue`.

**Convenções:**

| Item | Formato | Exemplo |
|---|---|---|
| Branch | `<prefixo>/<tema>-<numero>-<titulo>` | `chore/llm-config-1-setup-provider` |
| Worktree | `wts/<numero>-worktree-<tema>` | `wts/1-worktree-llm-config` |
| Doc de spec | `docs/issues-plans/issue-<numero>-<tema>.md` | `docs/issues-plans/issue-1-llm-config.md` |

Prefixos: `feat/` · `chore/` · `fix/` · `refactor/` · `docs/`

As worktrees ficam em `wts/` dentro do repo (ignorado pelo `.gitignore`). Para acessar uma worktree ativa:

```bash
# listar worktrees ativas
git worktree list

# entrar em uma worktree
cd wts/1-worktree-llm-config
```

Todo merge em `main` passa por PR com ao menos 1 aprovação — push direto está bloqueado.

---

## Checklist de Aprendizado

Cada item será rastreado como uma issue no repositório. O objetivo é cobrir todas as camadas da stack de ponta a ponta.

### LLM — Configuração central

- [x] Configurar provedor LLM (modelo, API key, parâmetros de tool use e streaming) via `.env` e `pydantic-settings` (#1)
- [x] Implementar invocação de tools pelo LLM (tool calling / function calling) (#2)
- [x] Tratar streaming de eventos LLM no backend (#3)

### Weather API

- [x] Registrar e configurar chave da WeatherAPI.com (#4, #14)
- [x] Criar tool `get_weather(city)` no backend consumindo a API (#5)

### Backend — Tools & MCP

- [x] Estruturar camada de tools chamáveis pelo LLM (roteamento, schemas, execução) (#6)
- [x] Expor tools via **MCP Server** (Model Context Protocol) no FastAPI (#7)
- [x] Implementar **BE CRUD** (entidade de exemplo end-to-end: model → schema → service → route) (#8)

### AG-UI — Protocolo agêntico

- [ ] Configurar **AG-UI Server** no backend (emissão de eventos de UI via streaming)
- [ ] Configurar **AG-UI Client** no frontend (consumo do stream e despacho de eventos para Signals)

### A2UI — Frontend agêntico

- [ ] Definir o **contrato do catálogo JSON** (schema que mapeia nomes de componentes para props A2UI)
- [ ] Implementar o **catálogo de componentes A2UI** (registro de componentes renderizáveis por nome)
- [ ] Construir o **componente de chat** (input do usuário + histórico de mensagens)
- [ ] Construir o **renderer A2UI** (lê eventos AG-UI via Signal e renderiza componentes do catálogo dinamicamente)

---

## Estado atual

- **Backend:** camada de tools (ToolRegistry), tool calling + streaming com LLM, tool `get_weather` (WeatherAPI.com), MCP Server em `/mcp`, CRUD de `Conversation` com SQLAlchemy + Alembic. ✅
- **Frontend:** app shell com toolbar Material, tema `azure-blue`, tipografia e animações habilitadas — aguardando integração AG-UI/A2UI.

**Próximos passos:** AG-UI Server (backend) → AG-UI Client (frontend) → catálogo A2UI + renderer.

**Branch ativa:**

| Branch | Descrição | Status |
|---|---|---|
| `docs/dev-script-and-readme-update` | dev.sh + READMEs atualizados | PR #21 aberta |
