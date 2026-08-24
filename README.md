# A2UI — POC Agêntica com AG-UI + Angular 21

POC de estudo explorando o uso combinado de **A2UI** (design system Angular Material) e **AG-UI Protocol** para construção de uma interface Angular verdadeiramente agêntica, onde componentes de UI são renderizados dinamicamente a partir de um catálogo JSON dirigido por um LLM via streaming.

O fluxo central é: usuário interage via chat → LLM escolhe tools (WeatherAPI, CRUD, etc.) → backend emite eventos AG-UI → frontend renderiza componentes A2UI reativamente via **Angular Signals**.

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | Angular 21 (standalone + Signals) + Angular Material |
| Backend | Python 3.11 / FastAPI |
| Protocolo agêntico | AG-UI (client + server) |
| LLM | Configurável via `.env` (OpenAI / Anthropic) |
| API externa | OpenWeatherMap (via tool call) |
| MCP | Tools expostas via MCP server no backend |

> **Por que Angular 21?** O projeto começou na v17, mas os SDKs oficiais necessários para as próximas partes do tutorial exigem versões mais novas: `@copilotkit/angular` exige Angular `^20 || ^21 || ^22`, e `@a2ui/angular` (SDK do protocolo A2UI da Google) exige `^21.2.5` — nenhuma versão publicada de nenhum dos dois suporta Angular 17. A migração foi feita de forma sequencial (`17 → 18 → 19 → 20 → 21`, via `ng update` a cada major, já que os schematics de migração automática só se aplicam passo a passo) na issue [#59](https://github.com/doljak-projects/A2UI_A17_Python/issues/59), validando build e testes a cada etapa. Angular 21 foi o alvo escolhido por ser a versão mínima que satisfaz os peer ranges dos dois SDKs simultaneamente, sem precisar ir até a 22.

## Estrutura

```
a2ui/
├── apps/
│   ├── frontend/   # Angular 21 + Angular Material (Design System)
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

## Frontend (Angular 21 + Material)

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

> Documentação completa do backend (endpoints, variáveis de ambiente, banco de dados, estrutura): [`apps/backend/README.md`](./apps/backend/README.md)

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

- [x] Configurar provedor LLM (modelo, API key, parâmetros de tool use e streaming) via `.env` e `pydantic-settings` ([#1](https://github.com/doljak-projects/A2UI_A17_Python/issues/1))
- [x] Implementar invocação de tools pelo LLM (tool calling / function calling) ([#2](https://github.com/doljak-projects/A2UI_A17_Python/issues/2))
- [x] Tratar streaming de eventos LLM no backend ([#3](https://github.com/doljak-projects/A2UI_A17_Python/issues/3))

### Weather API

- [x] Registrar e configurar chave da WeatherAPI.com ([#4](https://github.com/doljak-projects/A2UI_A17_Python/issues/4), [#14](https://github.com/doljak-projects/A2UI_A17_Python/issues/14))
- [x] Criar tool `get_weather(city)` no backend consumindo a API ([#5](https://github.com/doljak-projects/A2UI_A17_Python/issues/5))

### Backend — Tools & MCP

- [x] Estruturar camada de tools chamáveis pelo LLM (roteamento, schemas, execução) ([#6](https://github.com/doljak-projects/A2UI_A17_Python/issues/6))
- [x] Expor tools via **MCP Server** (Model Context Protocol) no FastAPI ([#7](https://github.com/doljak-projects/A2UI_A17_Python/issues/7))
- [x] Implementar **BE CRUD** (entidade de exemplo end-to-end: model → schema → service → route) ([#8](https://github.com/doljak-projects/A2UI_A17_Python/issues/8))

### Frontend — Chat base (sem AG-UI / A2UI)

- [x] `ChatService` — consumir `POST /api/chat` via SSE com Fetch streaming ([#24](https://github.com/doljak-projects/A2UI_A17_Python/issues/24))
- [x] `ChatComponent` — layout, estado com Signals e renderização de tokens em tempo real ([#25](https://github.com/doljak-projects/A2UI_A17_Python/issues/25))
- [x] Rota `/chat` e link de navegação na toolbar ([#26](https://github.com/doljak-projects/A2UI_A17_Python/issues/26))

### AG-UI — Protocolo agêntico

- [x] Configurar **AG-UI Server** no backend (emissão de eventos de UI via streaming)
- [x] Configurar **AG-UI Client** no frontend (consumo do stream e despacho de eventos para Signals)

**Tutorial A2UI Parte 1** ([`docs/tutorial_A2UI/01-ag-ui-sdk-typescript.md`](docs/tutorial_A2UI/01-ag-ui-sdk-typescript.md), baseado em [AG-UI in Practice: The SDK for TypeScript](https://www.angulararchitects.io/en/blog/ag-ui-in-practice-the-sdk-for-typescript/)) — **concluída**:

- [x] `[Back]` Esqueleto de agente (`AbstractAgent`) emitindo `RUN_STARTED`/`TEXT_MESSAGE_*`/`RUN_FINISHED` ([#32](https://github.com/doljak-projects/A2UI_A17_Python/issues/32)) — [como funciona (diagrama)](docs/diagrams/backend-agui-agent.md)
- [x] `[Front]` Consumir eventos do agente via `HttpAgent` + `AgentSubscriber` ([#34](https://github.com/doljak-projects/A2UI_A17_Python/issues/34)) — [como funciona (diagrama)](docs/diagrams/34-front-agui-http-agent.md)

**A estudar — Tutorial A2UI Parte 2** ([`docs/tutorial_A2UI/02-ag-ui-copilotkit-angular.md`](docs/tutorial_A2UI/02-ag-ui-copilotkit-angular.md), baseado em [Agentic UI with Angular, CopilotKit, and AG-UI](https://www.angulararchitects.io/en/blog/implementing-ag-ui-with-angular/)):

- [ ] `[Back]` Endpoint AG-UI com `POST` real, resolvendo o ciclo de tool call client-side ([#45](https://github.com/doljak-projects/A2UI_A17_Python/issues/45))
- [ ] `[Front]` Instalar e configurar o CopilotKit (`provideCopilotKit`) ([#46](https://github.com/doljak-projects/A2UI_A17_Python/issues/46))
- [ ] `[Front]` Agent store: `AppHttpAgent` + `initAgentStore` + `injectAgentStore` ([#47](https://github.com/doljak-projects/A2UI_A17_Python/issues/47))

### A2UI — Frontend agêntico

- [x] Definir o **contrato do catálogo JSON** (schema que mapeia nomes de componentes para props A2UI)
- [x] Implementar o **catálogo de componentes A2UI** (registro de componentes renderizáveis por nome)
- [x] Construir o **renderer A2UI** (lê eventos AG-UI via Signal e renderiza componentes do catálogo dinamicamente)

**Tutorial A2UI Parte 1** ([`docs/tutorial_A2UI/01-ag-ui-sdk-typescript.md`](docs/tutorial_A2UI/01-ag-ui-sdk-typescript.md)) — **concluída**:

- [x] `[Back]` Ligar a tool `get_weather` existente como server-side tool call do AG-UI ([#33](https://github.com/doljak-projects/A2UI_A17_Python/issues/33)) — [como funciona (diagrama)](docs/diagrams/backend-agui-agent.md)
- [x] `[Front]` Definir schema client-side (`Tool` + zod) de clima para renderização no chat ([#35](https://github.com/doljak-projects/A2UI_A17_Python/issues/35))
- [x] `[Front]` Ciclo de duas runs para resultado de tool call client-side ([#36](https://github.com/doljak-projects/A2UI_A17_Python/issues/36))

**A estudar — Tutorial A2UI Parte 2** ([`docs/tutorial_A2UI/02-ag-ui-copilotkit-angular.md`](docs/tutorial_A2UI/02-ag-ui-copilotkit-angular.md)):

- [ ] `[Front]` Tool de clima via `createFrontendTool`, sem o ciclo manual de duas runs ([#48](https://github.com/doljak-projects/A2UI_A17_Python/issues/48))
- [ ] `[Front]` Widget de clima renderizado via `copilot-render-tool-calls` ([#49](https://github.com/doljak-projects/A2UI_A17_Python/issues/49))
- [ ] `[Front]` UI de chat sidecar ligada ao agent store do CopilotKit ([#50](https://github.com/doljak-projects/A2UI_A17_Python/issues/50))

**A estudar — Tutorial A2UI Parte 3** ([`docs/tutorial_A2UI/03-google-a2ui-dynamic-ui.md`](docs/tutorial_A2UI/03-google-a2ui-dynamic-ui.md), protocolo **A2UI da Google** — nome coincide com o do projeto, mas são coisas diferentes; issues marcadas `-GOOGLE-A2UI-`):

- [x] `[Front]` Instalar e configurar o SDK A2UI (`@a2ui/angular`, `@a2ui/web_core`) ([#52](https://github.com/doljak-projects/A2UI_A17_Python/issues/52))
- [x] `[Front]` Renderizar card estático via `createSurface`/`updateComponents`/`updateDataModel` ([#53](https://github.com/doljak-projects/A2UI_A17_Python/issues/53))
- [x] `[Front]` Modelar o card de clima com o `WeatherToolResult` existente ([#54](https://github.com/doljak-projects/A2UI_A17_Python/issues/54))
- [x] `[Front]` Ação do cliente pra atualizar o card no lugar (`onAction`) ([#55](https://github.com/doljak-projects/A2UI_A17_Python/issues/55))

**Tutorial A2UI Parte 4** ([`docs/tutorial_A2UI/04-integrating-a2ui-with-ag-ui.md`](docs/tutorial_A2UI/04-integrating-a2ui-with-ag-ui.md), baseado em [Integrating A2UI with AG-UI and CopilotKit in Angular](https://www.angulararchitects.io/en/blog/integrating-a2ui-with-ag-ui-in-angular/)) — **concluída**:

- [x] `[Back]` Emitir operações A2UI dentro de um `ACTIVITY_SNAPSHOT` do agente de clima ([#72](https://github.com/doljak-projects/A2UI_A17_Python/issues/72))
- [x] `[Front]` `A2uiActivityRenderer` via a interface `ActivityRenderer` do CopilotKit ([#73](https://github.com/doljak-projects/A2UI_A17_Python/issues/73))
- [x] `[Front]` Renderizar o card de clima dentro do chat real via o activity renderer ([#74](https://github.com/doljak-projects/A2UI_A17_Python/issues/74))

**Tutorial A2UI Parte 5** ([`docs/tutorial_A2UI/05-custom-catalogs-in-a2ui.md`](docs/tutorial_A2UI/05-custom-catalogs-in-a2ui.md), baseado em [Custom Catalogs in A2UI](https://www.angulararchitects.io/en/blog/custom-catalogs-in-a2ui-your-own-components-for-ai-generated-uis/)) — **concluída**:

- [x] `[Front]` Componente customizado de clima (`HumidityGauge`) com schema Zod + `binding()` ([#75](https://github.com/doljak-projects/A2UI_A17_Python/issues/75))
- [x] `[Front]` Registrar catálogo customizado via `BasicCatalogBase` + `A2UI_RENDERER_CONFIG` ([#76](https://github.com/doljak-projects/A2UI_A17_Python/issues/76))
- [x] `[Front]` Usar o widget customizado no card de clima ([#77](https://github.com/doljak-projects/A2UI_A17_Python/issues/77))

**Tutorial A2UI Parte 6** ([`docs/tutorial_A2UI/06-a2ui-dashboard-performance.md`](docs/tutorial_A2UI/06-a2ui-dashboard-performance.md), baseado em [How I Made My A2UI Dashboard 300 Times Faster](https://www.angulararchitects.io/en/blog/how-i-made-my-a2ui-dashboard-300-times-faster/)) — **concluída**:

- [x] `[Back]` DSL compacta pra um mini-dashboard de clima, no lugar de markup A2UI completo ([#78](https://github.com/doljak-projects/A2UI_A17_Python/issues/78))
- [x] `[Back]` Conversão determinística DSL → A2UI no backend ([#79](https://github.com/doljak-projects/A2UI_A17_Python/issues/79))
- [x] `[Back]` Cache da estrutura gerada por hash da requisição ([#80](https://github.com/doljak-projects/A2UI_A17_Python/issues/80))

**Tutorial A2UI Parte 7** ([`docs/tutorial_A2UI/07-mcp-apps-fundamentals.md`](docs/tutorial_A2UI/07-mcp-apps-fundamentals.md), baseado em [Agentic UI with MCP Apps](https://www.angulararchitects.io/en/blog/agentic-ui-with-mcp-apps-tool-results-as-interactive-widgets/), protocolo **MCP Apps** — issues marcadas `-MCP-APPS-`) — **concluída**:

- [x] `[Back]` Investigar suporte a MCP Apps no SDK Python `mcp` e registrar o recurso de app da tool de clima ([#81](https://github.com/doljak-projects/A2UI_A17_Python/issues/81))
- [x] `[Front]` Host mínimo: iframe + `AppBridge` sobre `postMessage` ([#82](https://github.com/doljak-projects/A2UI_A17_Python/issues/82))
- [x] `[Front]` App mínimo: renderizar o widget a partir do input/resultado da tool ([#83](https://github.com/doljak-projects/A2UI_A17_Python/issues/83))

**Tutorial A2UI Parte 8** ([`docs/tutorial_A2UI/08-mcp-apps-angular-copilotkit.md`](docs/tutorial_A2UI/08-mcp-apps-angular-copilotkit.md), baseado em [MCP Apps in Angular with CopilotKit](https://www.angulararchitects.io/en/blog/mcp-apps-in-angular-with-copilotkit-rich-chat-interfaces-instead-of-text-responses/)) — **concluída**:

- [x] `[Back]` Emitir `ACTIVITY_SNAPSHOT` (`mcp-apps`) com o resultado da tool de clima ([#84](https://github.com/doljak-projects/A2UI_A17_Python/issues/84))
- [x] `[Back]` Middleware de proxy no backend pras requisições de recurso/tool do widget ([#85](https://github.com/doljak-projects/A2UI_A17_Python/issues/85))
- [x] `[Front]` `provideMCPApps()` em `app.config.ts` ([#86](https://github.com/doljak-projects/A2UI_A17_Python/issues/86))
- [x] `[Front]` Renderizar a atividade de MCP Apps no chat real ([#87](https://github.com/doljak-projects/A2UI_A17_Python/issues/87))

---

## Estado atual

As 8 partes do tutorial A2UI (`docs/tutorial_A2UI/`) estão **concluídas** — AG-UI, A2UI (protocolo Google), catálogo customizado, DSL de dashboard com cache e MCP Apps já estão todos integrados no chat real.

- **Backend:** camada de tools (ToolRegistry), tool calling + streaming com LLM, tool `get_weather` (WeatherAPI.com), MCP Server em `/mcp`, CRUD de `Conversation` com SQLAlchemy + Alembic, agente AG-UI emitindo `ACTIVITY_SNAPSHOT` (A2UI e MCP Apps) para o card de clima, DSL compacta → A2UI com cache por hash, middleware de proxy MCP Apps. ✅
- **Frontend:** app shell com toolbar Material, tema `azure-blue`; rota `/chat` unificada em torno do `<copilot-chat>` do `@copilotkit/angular` (chat antigo baseado em `ChatService`/SSE removido — [PR #94](https://github.com/doljak-projects/A2UI_A17_Python/pull/94)), com `A2uiActivityRenderer`, catálogo A2UI customizado (`HumidityGauge`) e widget MCP Apps todos operando lado a lado no mesmo chat. ✅
- **Em andamento (working tree, ainda sem issue/PR):** ajustes no agente e no card de clima A2UI — novo módulo `weather_intent.py` no backend e componente `temperature-hero` no frontend, além de refino visual do `HumidityGauge` e do `A2uiActivityRenderer`. Ainda não commitado.
