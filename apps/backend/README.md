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

## Variáveis de ambiente

Copie `.env.example` para `.env` e preencha **somente no `.env`**:

```bash
cp .env.example .env
```

> **Nunca coloque chaves reais no `.env.example`.** Ele é versionado e público.

| Variável | Obrigatória | Descrição |
|---|---|---|
| `LLM_PROVIDER` | Sim | `openai` ou `anthropic` |
| `LLM_API_KEY` | Sim | Chave de API do provedor LLM |
| `LLM_MODEL` | Sim | Ex.: `gpt-4o-mini` (OpenAI) ou `claude-3-5-sonnet-latest` (Anthropic) |
| `LLM_TEMPERATURE` | Não | Default `0.7` |
| `LLM_MAX_TOKENS` | Não | Default `1024` |
| `WEATHER_API_KEY` | Não* | Chave da [WeatherAPI.com](https://www.weatherapi.com/my/) — obrigatória para a tool `get_weather` |
| `WEATHER_BASE_URL` | Não | Default `https://api.weatherapi.com/v1` |
| `DATABASE_URL` | Não | Default `sqlite:///./a2ui.db` |
| `CORS_ORIGINS` | Não | Default `["http://localhost:4200"]` |

## Executar

```bash
uvicorn app.main:app --reload --port 8000
```

## Endpoints disponíveis

| Método | Path | Descrição |
|---|---|---|
| `GET` | `/api/health` | Health check — retorna status, nome e versão |
| `GET` | `/api/conversations` | Lista todas as conversas |
| `POST` | `/api/conversations` | Cria uma nova conversa |
| `GET` | `/api/conversations/{id}` | Retorna uma conversa pelo ID |
| `PATCH` | `/api/conversations/{id}` | Atualiza uma conversa |
| `DELETE` | `/api/conversations/{id}` | Remove uma conversa |
| `GET/POST` | `/mcp` | MCP Server (Streamable HTTP) — expõe tools do `ToolRegistry` |

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **MCP:** http://localhost:8000/mcp — configuração de cliente em [`docs/mcp.md`](../../docs/mcp.md)

## Exemplo: tool get_weather

A tool `get_weather` é chamada automaticamente pelo LLM quando o usuário pergunta sobre o clima. Ela consulta a [WeatherAPI.com](https://www.weatherapi.com/) e retorna temperatura, descrição e umidade.

**Via chat (SSE)** — o LLM decide invocar a tool e devolve a resposta em streaming:

```bash
curl -N -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Qual o clima em São Paulo agora?"}
    ]
  }'
```

Resposta esperada (eventos SSE):
```
data: {"type": "text_delta", "data": {"delta": "O clima em São Paulo agora é "}}
data: {"type": "text_delta", "data": {"delta": "de 22°C, parcialmente nublado, umidade de 68%."}}
data: {"type": "message_stop", "data": {}}
```

**Via MCP** — invoca a tool diretamente sem passar pelo LLM:

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "get_weather",
      "arguments": {"city": "Lisboa"}
    },
    "id": 1
  }'
```

Resposta:
```json
{
  "city": "Lisboa",
  "temperature_c": 24.1,
  "description": "Sunny",
  "humidity": 55
}
```

> Requer `WEATHER_API_KEY` preenchida no `.env`. Sem a chave, ambas as chamadas retornam erro 500.

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
