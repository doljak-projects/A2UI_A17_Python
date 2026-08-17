---
tutorial_part: 7
source_title: "Agentic UI with MCP Apps: Tool Results as Interactive Widgets"
source_url: https://www.angulararchitects.io/en/blog/agentic-ui-with-mcp-apps-tool-results-as-interactive-widgets/
source_series: "Agentic UI with Angular (Angular Architects) — artigo 9 de 10"
status: draft
last_updated: 08-17-2026
---

# Tutorial A2UI — Parte 7: fundamentos de MCP Apps

> Documento agnóstico: escrito para ser lido tanto por humanos quanto por outras IAs que venham a continuar este trabalho no projeto A2UI. Cada passo abaixo tem uma issue equivalente no GitHub.

## ⚠️ Aviso de nomenclatura e risco técnico

**MCP Apps é um protocolo diferente do A2UI da Google** (Partes 3/5/6) e do AG-UI (Partes 1/2/4) — por isso ganha marcador próprio, `-MCP-APPS-`. Enquanto o A2UI da Google faz o **LLM gerar** a estrutura de UI em runtime, o MCP Apps é **declarativo**: a metadata de uma tool MCP aponta (`resourceUri`) pra um recurso HTML fixo (o "app"/widget), registrado no servidor de antemão — o LLM não gera markup nenhum, só decide *quando* chamar a tool.

**Risco técnico identificado:** o exemplo do artigo usa o SDK JS/Node (`@modelcontextprotocol/ext-apps/server`, `registerAppTool`, `registerAppResource`). O backend deste projeto expõe MCP via **Python** (`app/mcp/server.py`, issue #7), e não há confirmação de que o SDK Python `mcp` tenha uma extensão equivalente a `ext-apps`. **O Passo 1 abaixo é, portanto, uma investigação antes de ser implementação** — se o SDK Python não suportar isso nativamente, o passo 1 implementa a mecânica manualmente (servir o HTML como um recurso comum do MCP Server, com metadata seguindo o formato `{ ui: { resourceUri } }` do spec), sem inventar uma API Python que não existe.

## 1. Resumo geral

MCP (Model Context Protocol) tradicional retorna de uma tool "texto plano ou dados estruturados, que o agente apresenta como uma mensagem de chat simples" — MCP Apps estende isso permitindo que "o resultado de uma tool apareça como um widget sob medida em vez de uma parede de texto". A mecânica: a metadata da tool aponta, via `resourceUri` (ex: `"ui://hotels/results.html"`), pro arquivo HTML do widget; um **host** (quem hospeda o chat) cria um `<iframe sandbox>` carregando esse HTML e conecta um `AppBridge` (lado host) a um `App` (lado widget, dentro do iframe) via `postMessage`. O host manda `sendToolInput()`/`sendToolResult()`/`sendHostContextChange()` (tema, modo de exibição); o widget escuta via `ontoolinput`/`ontoolresult`/`onhostcontextchanged` e se renderiza com os dados recebidos — sem re-fazer a chamada da tool.

### Por que isso importa para o A2UI (o projeto)

O projeto já tem um servidor MCP funcionando (`app/mcp/server.py`, issue #7) expondo `get_weather` — esta Parte 7 é o primeiro passo pra fazer o **resultado** dessa tool aparecer como um widget interativo (não só JSON cru), antes de integrar isso ao chat real do Angular (Parte 8).

## 2. Conceitos-chave do artigo

| Conceito | O que é |
|---|---|
| `resourceUri` | Campo na metadata da tool MCP apontando pro arquivo HTML do widget (ex: `ui://weather/card.html`) |
| `AppBridge` | Objeto lado **host**, gerencia a conexão com o app embutido via `postMessage` |
| `App` | Objeto lado **widget** (dentro do iframe), recebe input/resultado da tool e contexto do host |
| `PostMessageTransport` | Camada de transporte que implementa a comunicação `postMessage` bidirecional entre host e app |
| `sendToolInput()` / `sendToolResult()` | Métodos do host que mandam os parâmetros e o resultado da tool pro widget |
| `sendHostContextChange()` | Método do host que manda tema, modo de exibição e variáveis CSS pro widget |
| `onsizechange` | Evento do widget avisando o host pra redimensionar o iframe (evita scrollbar) |
| `teardownResource()` / `requestTeardown()` | Mecanismo de encerramento ordenado, com oportunidade de salvar estado antes de fechar |
| iframe `sandbox` | Isolamento de segurança do widget (`allow-scripts`, `allow-same-origin`) |

## 3. Passos didáticos e issues equivalentes

### Passo 1 — Investigar e registrar o recurso de app da tool `get_weather`
Verificar se o SDK Python `mcp` (usado em `app/mcp/server.py`) tem suporte nativo a MCP Apps (extensão equivalente a `ext-apps`). Se sim, usar a API nativa para registrar o widget HTML como recurso associado à tool `get_weather`, com `resourceUri` (ex: `ui://weather/card.html`). Se não, implementar manualmente: servir o HTML como um recurso comum do MCP Server e anexar a metadata `{ ui: { resourceUri } }` à definição da tool, seguindo o formato do spec MCP Apps mesmo sem biblioteca dedicada. Documentar no doc da issue qual dos dois caminhos foi necessário.

- **Issue:** [#81 — `[Back] -MCP-APPS- Investigate MCP Apps support in the Python mcp SDK and register the weather tool's app resource`](https://github.com/doljak-projects/A2UI_A17_Python/issues/81)

### Passo 2 — Host mínimo: iframe + AppBridge
Construir uma página de demo isolada (frontend, sem integração com o chat/CopilotKit ainda) que cria um `<iframe sandbox="allow-scripts allow-same-origin">` apontando pro widget HTML do Passo 1, inicializa um `AppBridge` sobre um `PostMessageTransport`, e manda `sendToolInput({ city: 'São Paulo' })` seguido de `sendToolResult({ content, structuredContent })` com um resultado mockado de `WeatherToolResult`. Trata `onsizechange` pra redimensionar o iframe.

- **Issue:** [#82 — `[Front] -MCP-APPS- Minimal host page with iframe + AppBridge over postMessage`](https://github.com/doljak-projects/A2UI_A17_Python/issues/82)

### Passo 3 — App mínimo: renderizar o widget a partir do input/resultado recebido
Implementar o HTML/JS do widget (`weather/card.html`, servido pelo Passo 1): instancia um `App`, registra `ontoolinput`/`ontoolresult` pra capturar os dados mandados pelo host, e renderiza o card de clima (city/temperature_c/description/humidity) em HTML/CSS puro, sem framework — igual o artigo faz (VanillaJS, sem agente/LLM envolvido, pra isolar a mecânica host↔app).

- **Issue:** [#83 — `[Front] -MCP-APPS- Minimal app page rendering the weather widget from tool input/result`](https://github.com/doljak-projects/A2UI_A17_Python/issues/83)

## 4. O que fica para depois

Esta parte fica deliberadamente isolada do Angular/CopilotKit/agente real — é só a mecânica host↔app funcionando com dados mockados. A integração de verdade (servidor MCP real, agente decidindo chamar a tool, renderização dentro do chat Angular) é a Parte 8.
