---
issue: 47
title: "[Front] -AG-UI- Agent store: AppHttpAgent, initAgentStore and injectAgentStore"
branch: feat/copilotkit-agent-store-47-init
status: closed
last_updated: 08-15-2026
---

# Issue #47 — Agent store: AppHttpAgent, initAgentStore and injectAgentStore

## Objective
Register the AG-UI weather agent (endpoint `POST /api/agui/weather-tool-agent-demo`, issue #45) with CopilotKit's runtime, and expose it as an `AgentStore` (`isRunning()`/`messages()` signals) via a single injectable entry point — laying the ground for issues #48–#50.

## Scope
- Register the weather agent via `CopilotKit.updateRuntime({ selfManagedAgents })`
- Expose `injectWeatherAgentStore()` returning `injectAgentStore('weather-agent')`
- Reference: `docs/tutorial_A2UI/02-ag-ui-copilotkit-angular.md` (Passo 3)

## Decisão de arquitetura: sem `AppHttpAgent`
O `.d.ts` de `@copilotkit/angular@0.3.1` foi conferido antes de codar: `HttpAgent` (do `@ag-ui/client`) já monta `POST` com o `RunAgentInput` completo no corpo por padrão — exatamente o que o endpoint da issue #45 espera. Diferente do `AguiGetHttpAgent` (issue #34), que precisava sobrescrever `requestInit()` pra forçar `GET` sem corpo nos endpoints antigos, aqui **nenhuma customização é necessária**. Decisão explícita do usuário: não criar uma subclasse `AppHttpAgent` vazia só por fidelidade ao nome do tutorial — usar `HttpAgent` puro, evitando boilerplate sem função real.

Também não existe um `initAgentStore` pronto exportado pelo SDK — o que existe é o serviço injetável `CopilotKit` com o método `updateRuntime({ selfManagedAgents })`. `initAgentStore()` é uma função interna do arquivo (não exportada) que encapsula essa chamada, é idempotente (`copilotKit.getAgent(id)` evita recriar o `HttpAgent` numa segunda injeção) e é usada só internamente por `injectWeatherAgentStore()`.

## Status
> Atualizado em: 2026-08-15

- [x] `apps/frontend/src/app/core/services/weather-agent-store.ts` criado: `initAgentStore()` (privada, registra `HttpAgent` sob o id `weather-agent` apontando pra `${environment.apiBaseUrl}/agui/weather-tool-agent-demo`) + `injectWeatherAgentStore()` (pública, chama `initAgentStore()` e devolve `injectAgentStore('weather-agent')` do SDK).
- [x] `ng build` limpo (mesmos warnings pré-existentes de budget/CommonJS da issue #46).
- [x] Spec `weather-agent-store.spec.ts` criado — 3 casos: agente registrado como `HttpAgent` na URL correta, `AgentStore` devolvido com `isRunning()`/`messages()` como signals, idempotência (segunda injeção não recria o agente). `ng test` completo: 39/42 verdes, mesmas 3 falhas pré-existentes de `agui-test.component.spec.ts`, sem regressão nova.

## Notes
- Nenhuma UI consome o store ainda — isso é a issue #50 (sidecar chat). As issues #48/#49 (tool client-side + widget) também dependem deste agent store já registrado.
- Warning `'Agent weather-agent not found'` aparece no console durante os testes (efeito colateral de leitura do signal antes do registro síncrono completar dentro do mesmo `detectChanges()`); não é um erro — os 3 casos passam e o comportamento funcional está correto.
