---
issue: 35
title: "[Front] -A2UI- Define client-side weather Tool schema for chat rendering"
branch: feat/weather-tool-schema-35-client-side-definition
status: ready-for-review
last_updated: 2026-08-01
---

# Issue #35 — Define client-side weather Tool schema for chat rendering

## Objective
Define a client-side `Tool` (from `@ag-ui/client`) describing, via a `zod` schema, the weather data shape the client knows how to render (condition, temperature, wind), and register it when calling `runAgent`. Prepare (without finalizing UI) the data structure that will feed the weather card display in `ChatComponent` (issue #25).

## Scope
- Define a `zod` schema for weather data (`condition`, `temperature`, `wind`)
- Export a `Tool` object (`showWeatherTool`) built from that schema via `z.toJSONSchema(...)`
- Register the tool in the `runAgent({ tools: [...] })` call
- Prepare the data shape to be consumed by `ChatComponent` for rendering
- Reference: `docs/tutorial_A2UI/01-ag-ui-sdk-typescript.md` (Passo 4)

## Modo de trabalho desta issue
Segue o mesmo formato mentorado da issue #34: antes de cada trecho de código, o conceito/decisão é explicado, o usuário confirma entendimento, só então o código é escrito — passos pequenos, um de cada vez. Decisões de implementação (racional, alternativas descartadas) são registradas neste doc, não só na conversa.

## Status
> Atualizado em: 2026-08-01

- [x] Passo 1 — Schema/Tool vão morar em arquivo próprio (isolado de `ChatService`/`ChatComponent`, seguindo o padrão de #34, local a definir no Passo 2). `zod` adicionado como dependência **direta** em `apps/frontend/package.json` (`^3.22.4`, mesma faixa já resolvida via `@ag-ui/client`) — decisão do usuário: depender apenas da transitiva é frágil porque diferentes pacotes no projeto podem evoluir/versionar `zod` de forma independente, e uma troca de versão do `@ag-ui/client` poderia remover/alterar essa dependência sem aviso.
- [x] Passo 2 — Schema `zod` definido em `core/services/weather-tool-for-a2ui.ts` (`weatherSchema`), com campos `city`/`temperature_c`/`description`/`humidity` (nomes do backend, não os do tutorial) — ver `## Decisões de implementação`
- [x] Passo 3 — `showWeatherTool` (`Tool` do `@ag-ui/core`) exportado no mesmo arquivo, construído via `z.toJSONSchema(weatherSchema)` — ver `## Decisões de implementação` sobre o import de `zod/v4`
- [x] Passo 4 — `showWeatherTool` registrado em `agent.runAgent({ tools: [showWeatherTool] })` dentro de `AguiTestComponent.runAgent()` (ponto de entrada da #34). O endpoint de demo (`weather-tool-demo`) ainda não inspeciona `tools` no backend — é só preparação mecânica, sem efeito funcional visível ainda.
- [x] Passo 5 — `parseWeatherToolResult(content: string): WeatherToolResult` adicionado em `weather-tool-for-a2ui.ts`, validando/parseando o JSON bruto de um `ToolCallResultEvent` contra `weatherSchema`. Nenhuma UI/template criado — só o dado tipado, pronto para o card de clima (issue #36).
- [x] Passo 6 — Testes: `weather-tool-for-a2ui.spec.ts` (novo — cobre `weatherSchema`, `showWeatherTool`/JSON Schema gerado e `parseWeatherToolResult`, sucesso e falha) e `agui-test.component.spec.ts` (ajustado — confirma `runAgent` chamado com `{ tools: [showWeatherTool] }`). 10/10 verdes nos arquivos da issue; suíte completa 32/35 (as 3 falhas são as mesmas pré-existentes de `chat.component.spec.ts`, não relacionadas). Validação manual: usuário faz por conta própria.

## Decisões de implementação

> Racional por trás das escolhas de cada passo — para quem (humano ou IA) retomar este trabalho sem o contexto da conversa original.

**Por que `zod` como dependência direta, não só transitiva (Passo 1)**
`zod` já existia no projeto apenas como dependência transitiva do `@ag-ui/client` (não declarada em `apps/frontend/package.json`). Como este arquivo importa `zod` diretamente, declará-lo explícito é mais seguro: diferentes pacotes do projeto podem evoluir/versionar `zod` de forma independente, e uma troca de versão do `@ag-ui/client` no futuro poderia remover ou alterar essa dependência transitiva sem aviso, quebrando nosso build silenciosamente. Adicionado `"zod": "^3.22.4"` (mesma faixa já resolvida) e rodado `npm install` para registrar no lockfile.

**Por que `weather-tool-for-a2ui.ts` como nome de arquivo (Passo 1)**
Seguindo a convenção de nomenclatura do projeto (`-AG-UI-` = mecânica do protocolo/SDK, reaproveitável em qualquer projeto; `-A2UI-` = integração específica deste projeto — ver `docs/tutorial_A2UI/01-ag-ui-sdk-typescript.md`), este arquivo é claramente A2UI: os nomes de campo do schema vêm do `get_weather` real do backend, não são genéricos do protocolo AG-UI. Por indicação do usuário, o nome do arquivo deixa esse contraste explícito (`weather-tool-for-a2ui.ts`), diferente dos arquivos AG-UI genéricos da issue #34 (`agui-*.ts`).

**Por que os nomes de campo batem com o backend, não com o tutorial (Passo 2)**
O tutorial original usa `condition`/`temperature`/`wind`. O backend real (`app/schemas/weather.py`, `WeatherResult`) devolve `city`/`temperature_c`/`description`/`humidity`, em **snake_case** (confirmado no JSON real de `GET /api/agui/weather-tool-demo`: `{"city":"São Paulo","temperature_c":24.7,"description":"Ensolarado","humidity":35}`). Decisão do usuário: usar os nomes do backend, exatamente como aparecem no JSON — evita uma camada de mapeamento/tradução quando a issue #36 conectar esse schema ao resultado real da tool call.

**Por que `zod/v4`, não o `zod` default (Passo 3)**
A issue pede explicitamente `z.toJSONSchema(...)`, mas essa API só existe no Zod v4 — o pacote `zod` instalado (`3.25.76`) é uma versão de transição que empacota **v3 e v4 juntos**; o import padrão `from 'zod'` resolve para v3 (sem `toJSONSchema`), enquanto `from 'zod/v4'` expõe a API v4 completa, incluindo `toJSONSchema`, sem precisar instalar nada além do que já está no `package.json`. Como nada mais no projeto usa `zod` ainda, e o campo `parameters` do tipo `Tool` do `@ag-ui/core` é tipado como `z.ZodAny` (aceita qualquer objeto JSON Schema, sem acoplamento de versão do zod), não há conflito em usar `zod/v4` isolado neste arquivo.

## Notes
- A issue #33 (backend) já expõe clima real via `GET /api/agui/weather-tool-demo`, mas resolve a tool call **server-side**. Esta issue (#35) é sobre o schema **client-side** — a tool nem precisa ser chamada pelo servidor ainda; o objetivo é o schema existir e estar registrado.
- Campos do schema (`condition`, `temperature`, `wind`) não batem 1:1 com o que `get_weather` do backend retorna (`city`, `temperature_c`, `description`, `humidity`) — isso é esperado, o tutorial usa esse shape específico como exemplo didático; avaliar no Passo 2 se ajustamos os nomes para casar com o backend ou seguimos literalmente o tutorial.
- `ChatService`/`ChatComponent` existentes **não são tocados** nesta issue.
