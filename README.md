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

---

## Checklist de Aprendizado

Cada item será rastreado como uma issue no repositório. O objetivo é cobrir todas as camadas da stack de ponta a ponta.

### LLM — Configuração central

- [ ] Configurar provedor LLM (modelo, API key, parâmetros de tool use e streaming) via `.env` e `pydantic-settings`
- [ ] Implementar invocação de tools pelo LLM (tool calling / function calling)
- [ ] Tratar streaming de eventos LLM no backend

### Weather API

- [ ] Registrar e configurar chave da OpenWeatherMap
- [ ] Criar tool `get_weather(city)` no backend consumindo a API

### Backend — Tools & MCP

- [ ] Estruturar camada de tools chamáveis pelo LLM (roteamento, schemas, execução)
- [ ] Expor tools via **MCP Server** (Model Context Protocol) no FastAPI
- [ ] Implementar **BE CRUD** (entidade de exemplo end-to-end: model → schema → service → route)

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

- Frontend: app shell com toolbar Material, tema `azure-blue`, tipografia e animações habilitadas, página inicial de exemplo.
- Backend: estrutura base do FastAPI com endpoint `GET /api/health`, configuração via `pydantic-settings` e teste inicial.
