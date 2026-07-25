# MCP Server

O backend expõe as tools do `ToolRegistry` via **MCP** (Model Context Protocol), usando o
transporte **Streamable HTTP** do SDK oficial Python. Qualquer cliente MCP (Cursor, Claude
Desktop, um script Python) consegue listar e invocar as tools do backend.

## Endpoint

| Item | Valor |
|---|---|
| URL | `http://127.0.0.1:8000/mcp` |
| Transporte | Streamable HTTP (SSE) |
| Autenticação | nenhuma (servidor local de desenvolvimento) |

A rota vive dentro da mesma app FastAPI da API REST — não há processo separado. Como o path
é registrado exato, use `/mcp` **sem** barra final.

Subir o servidor:

```bash
cd apps/backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

## Tools expostas

O servidor MCP não redeclara tools: ele lê o `ToolRegistry` a cada `tools/list`. Registrar
uma tool nova em `app/tools/` (via `registry.register(...)`) já a torna visível no MCP, sem
tocar em `app/mcp/server.py`.

Hoje o registry padrão traz:

- `echo(message)` — devolve a mensagem recebida.
- `get_weather(city)` — clima atual da cidade (exige `WEATHER_API_KEY` no `.env`; a chave só
  é necessária na execução, a tool aparece na listagem de qualquer forma).

## Conectar um cliente

### Cursor

Em `.cursor/mcp.json` (do projeto) ou `~/.cursor/mcp.json` (global):

```json
{
  "mcpServers": {
    "a2ui-backend": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

### Claude Desktop

O Claude Desktop fala **stdio**, então precisa da ponte `mcp-remote` para alcançar um
servidor HTTP. Em `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "a2ui-backend": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://127.0.0.1:8000/mcp"]
    }
  }
}
```

Em ambos os casos o backend precisa estar rodando **antes** de o cliente iniciar.

## Testar rapidamente

Com o servidor no ar, este script conecta, lista as tools e invoca a `echo`:

```python
import anyio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main() -> None:
    async with streamablehttp_client("http://127.0.0.1:8000/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            for tool in (await session.list_tools()).tools:
                print(tool.name, "-", tool.description)

            result = await session.call_tool("echo", {"message": "MCP funcionando"})
            print(result.structuredContent)


anyio.run(main)
```

Saída esperada:

```
echo - Retorna de volta a mensagem recebida.
get_weather - Consulta as condições climáticas atuais de uma cidade. (...)
{'message': 'MCP funcionando'}
```

Para um teste sem cliente MCP, o handshake `initialize` responde via `curl`:

```bash
curl -sN http://127.0.0.1:8000/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{
        "protocolVersion":"2025-06-18","capabilities":{},
        "clientInfo":{"name":"curl","version":"1.0"}}}'
```

## Implementação

- `app/mcp/server.py` — `build_mcp_server(registry=None)` monta o servidor MCP a partir do
  registry (o parâmetro existe para os testes usarem um registry isolado);
  `build_session_manager()` cria o session manager do transporte; `add_mcp_route()` publica
  a rota no FastAPI.
- `app/main.py` — `create_app()` inicia o session manager no `lifespan`. Isso não é
  opcional: sem o `run()` ativo, a primeira requisição em `/mcp` falha com
  *"Task group is not initialized"*.

Erros de tool viram `CallToolResult` com `isError=true` (tool inexistente, argumentos fora
do JSON Schema ou exceção durante a execução), em vez de derrubar a conexão.
