---
tutorial_part: 8
source_title: "MCP Apps in Angular with CopilotKit: Rich Chat Interfaces Instead of Text Responses"
source_url: https://www.angulararchitects.io/en/blog/mcp-apps-in-angular-with-copilotkit-rich-chat-interfaces-instead-of-text-responses/
source_series: "Agentic UI with Angular (Angular Architects) — artigo 10 de 10"
status: draft
last_updated: 08-17-2026
---

# Tutorial A2UI — Parte 8: MCP Apps no Angular com CopilotKit

> Documento agnóstico: escrito para ser lido tanto por humanos quanto por outras IAs que venham a continuar este trabalho no projeto A2UI. Cada passo abaixo tem uma issue equivalente no GitHub.

## Dependência da Parte 7

Este artigo é o último da série e assume a mecânica host↔app da Parte 7 (`AppBridge`/`App`/`postMessage`, `teardownResource`) como conhecida — o texto original diz: "In the previous article, we laid the foundations of MCP and MCP Apps". Aqui, essa mecânica é encapsulada pelo renderer de MCP Apps do próprio CopilotKit (`provideMCPApps`), então não é reimplementada — é a Parte 7 que dá o entendimento de baixo nível do que o CopilotKit está fazendo por baixo dos panos.

## ⚠️ Risco técnico (mesmo da Parte 7)

O artigo usa `@ag-ui/mcp-apps-middleware` (`MCPAppsMiddleware`) e o framework de agente **Mastra** (Node) pro proxy backend. O backend deste projeto é **Python/FastAPI**, sem equivalente confirmado a esse middleware. Os passos `[Back]` abaixo precisam implementar o proxy manualmente (rotear requisições de recurso/tool do widget pro servidor MCP configurado), seguindo o *comportamento* descrito no artigo, não a biblioteca Node específica.

## 1. Resumo geral

Este artigo mostra a integração de produção: um servidor MCP expõe uma tool com widget associado (`registerAppTool`/`registerAppResource`, Parte 7); quando o agente executa essa tool, o backend empacota a metadata do widget e o resultado estruturado num evento AG-UI `ACTIVITY_SNAPSHOT` (`activityType: 'mcp-apps'`) — o mesmo mecanismo de transporte da Parte 4, mas para MCP Apps em vez de A2UI da Google. O CopilotKit Angular (`provideMCPApps()`) já vem com um `ActivityRenderer` pronto para esse `activityType`: ele carrega o widget num iframe seguro e faz o proxy das requisições de recurso/tool do widget de volta pro backend (`MCPAppsMiddleware`), evitando expor o servidor MCP diretamente ao browser.

### Por que isso importa para o A2UI (o projeto)

É o equivalente, para MCP Apps, do que a Parte 4 fez para o A2UI da Google: sair da demo isolada (Parte 7) e renderizar o widget de clima dentro do chat sidecar real (issue #50), ao lado do card A2UI já existente — dois mecanismos de UI agêntica coexistindo no mesmo chat.

## 2. Conceitos-chave do artigo

| Conceito | O que é |
|---|---|
| `ACTIVITY_SNAPSHOT` (`activityType: 'mcp-apps'`) | Mesmo tipo de evento AG-UI da Parte 4, mas carregando metadata de tool MCP Apps + resultado estruturado |
| `provideMCPApps()` | Config do CopilotKit Angular que registra o `ActivityRenderer` de MCP Apps pronto (equivalente ao `A2uiActivityRenderer` que construímos à mão na Parte 4, mas oferecido pelo SDK) |
| `MCPAppsConfig` (`hostInfo`/`hostContext`) | Identidade do host e regras de apresentação (tema, modo de exibição) mandadas pro widget |
| Middleware de proxy | Componente backend que roteia requisições de recurso/tool do widget pro servidor MCP configurado, sem expor o MCP Server diretamente ao cliente |
| `CopilotActivity` / roteamento por `activityType` | Componente que escolhe entre o renderer de A2UI (Parte 4) e o de MCP Apps (esta parte) conforme o `activityType` da mensagem |

## 3. Passos didáticos e issues equivalentes

Convenção: `-MCP-APPS-` para todos — mecânica do protocolo aplicada especificamente à integração com este projeto.

### Passo 1 — Emitir um ACTIVITY_SNAPSHOT com o resultado da tool de clima
No `WeatherToolCallAgent` (backend), ao executar `get_weather` com o widget registrado na Parte 7, empacotar `resourceUri` + resultado estruturado (`WeatherToolResult`) num evento AG-UI `ACTIVITY_SNAPSHOT` com `activityType: 'mcp-apps'` — reaproveitando o mesmo padrão de transporte já implementado na Parte 4 (Passo 1), agora para um payload de MCP Apps em vez de A2UI.

- **Issue:** [#84 — `[Back] -MCP-APPS- Emit an ACTIVITY_SNAPSHOT (mcp-apps) with the weather MCP App's tool result`](https://github.com/doljak-projects/A2UI_A17_Python/issues/84)

### Passo 2 — Middleware de proxy no backend
Implementar (manualmente, dado o risco técnico documentado acima) um middleware/rota no FastAPI que detecta requisições de recurso/tool vindas do widget (iframe) e as roteia pro servidor MCP interno (`app/mcp/server.py`, issue #7) — sem o cliente precisar falar diretamente com o MCP Server.

- **Issue:** [#85 — `[Back] -MCP-APPS- Backend proxy middleware routing widget resource/tool requests`](https://github.com/doljak-projects/A2UI_A17_Python/issues/85)

### Passo 3 — Configurar `provideMCPApps()` no Angular
Registrar `provideMCPApps({ hostInfo, hostContext })` em `app.config.ts`, definindo identidade do host e contexto de apresentação (tema, modo de exibição) — ao lado dos providers já existentes de CopilotKit (issue #46) e A2UI (issue #52).

- **Issue:** [#86 — `[Front] -MCP-APPS- provideMCPApps() config in app.config.ts`](https://github.com/doljak-projects/A2UI_A17_Python/issues/86)

### Passo 4 — Renderizar o widget de MCP Apps no chat real
Atualizar o roteamento de atividades do chat (o mesmo `<app-copilot-activity>`/`CopilotActivity` construído na Parte 4, Passo 3) para também reconhecer `activityType: 'mcp-apps'` e delegar pro renderer do `provideMCPApps()`. Validação: pedir o clima no chat sidecar real deve poder mostrar tanto o card A2UI (Parte 4) quanto o widget MCP Apps (dependendo de qual caminho o agente escolher), sem conflito entre os dois mecanismos.

- **Issue:** [#87 — `[Front] -MCP-APPS- Render the MCP Apps activity in the real chat UI`](https://github.com/doljak-projects/A2UI_A17_Python/issues/87)

## 4. O que fica para depois

Esta é a última parte planejada da série de 10 artigos da Angular Architects. Não há "Parte 9" prevista além destas — próximos temas de tutorial precisariam ser definidos a partir de necessidades novas do projeto, não de mais artigos desta série específica.
