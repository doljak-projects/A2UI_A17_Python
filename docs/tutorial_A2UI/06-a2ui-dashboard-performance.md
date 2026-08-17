---
tutorial_part: 6
source_title: "How I Made My A2UI Dashboard 300 Times Faster"
source_url: https://www.angulararchitects.io/en/blog/how-i-made-my-a2ui-dashboard-300-times-faster/
source_series: "Agentic UI with Angular (Angular Architects) — artigo 8 de 10"
status: draft
last_updated: 08-17-2026
---

# Tutorial A2UI — Parte 6: dashboards A2UI mais rápidos (DSL + cache)

> Documento agnóstico: escrito para ser lido tanto por humanos quanto por outras IAs que venham a continuar este trabalho no projeto A2UI. Cada passo abaixo tem uma issue equivalente no GitHub.

## ⚠️ Nota de escopo

Diferente das outras partes, esta **não é uma otimização de Angular** (sem signals/change detection/virtualização) — é uma otimização de **arquitetura de geração**: o gargalo do artigo original está inteiramente na forma como o LLM gera a estrutura A2UI, não em como o Angular renderiza. Além disso, o benchmark do artigo (~40s → ~0.1s, 46 mil → 1.500 tokens) depende de um dashboard com múltiplos tiles gerado ao vivo por um LLM — o projeto ainda só tem um único card de clima determinístico (issue #54), então o primeiro passo aqui precisa estabelecer esse cenário antes de otimizá-lo.

## 1. Resumo geral

O artigo descreve um dashboard (dados de viagem: passagens, voos, hotéis, carros, clima) gerado via A2UI que levava ~40 segundos e consumia 46 mil+ tokens por renderização. A causa: o LLM era forçado a gerar a estrutura A2UI inteira, token a token, a partir de um prompt few-shot enorme (43 mil tokens de exemplos), além de orquestrar múltiplas tool calls de dados no mesmo passo de raciocínio.

A solução: introduzir uma **DSL específica da aplicação** — um JSON compacto (`{ tiles: [{ type: 'boardingPasses', count: 2 }, ...] }`) que o LLM produz em vez da estrutura A2UI completa. Duas etapas determinísticas, fora do LLM, cuidam do resto: (1) código server-side converte a DSL em `updateComponents` real; (2) os dados são buscados a partir dos tipos de tile pedidos. Isso já reduz o custo ~30x (a saída do modelo fica muito menor). Uma segunda otimização usa a separação nativa do protocolo A2UI entre **estrutura** (`updateComponents`) e **dados** (`updateDataModel`): a estrutura é cacheada por um hash da descrição do usuário, e em cache-hit só o `updateDataModel` (com dados frescos) é reenviado — o LLM é completamente pulado nesse caso, chegando ao resultado final de ~300x mais rápido / ~30x menos tokens.

### Por que isso importa para o A2UI (o projeto)

O card de clima atual é montado 100% em código (`createWeatherCard()`), sem LLM gerando estrutura nenhuma — então tecnicamente já não tem esse problema. Mas a técnica da DSL é o caminho natural para quando o projeto quiser um dashboard com **múltiplos** widgets decididos dinamicamente pelo agente (ex: "mostra o clima de 3 cidades" vs. hoje, que é sempre 1 card fixo) sem reintroduzir o custo de geração token-a-token.

## 2. Conceitos-chave do artigo

| Conceito | O que é |
|---|---|
| DSL específica da aplicação | Formato JSON minimalista e restrito (schema de tool, ex: `renderDashboard`) que limita a saída do LLM a "quais tiles, com quais parâmetros" — não a estrutura A2UI inteira |
| Separação estrutura/dados | `updateComponents` (estrutura, cacheável) vs. `updateDataModel` (dados, sempre frescos) — dois ciclos de vida independentes no protocolo A2UI |
| Geração determinística de código | Conversão DSL → A2UI feita em código comum (sem LLM) — elimina variância e erros de markup gerados token a token |
| Cache por hash | Hash da descrição textual do usuário (ou de um identificador de dashboard) usado como chave de cache pra DSL e pra estrutura A2UI derivada |

## 3. Passos didáticos e issues equivalentes

Convenção: `-GOOGLE-A2UI-`, já que a técnica (DSL + cache de estrutura) é mecânica de protocolo, reaproveitável em qualquer projeto A2UI — não é algo específico deste projeto além do domínio de clima usado como exemplo.

### Passo 1 — DSL compacta para um mini-dashboard de clima
Definir uma tool `renderWeatherDashboard` com schema DSL restrito (ex: `{ cities: string[] }`, ou `{ tiles: [{ type: 'currentWeather', city }, { type: 'forecast', city }] }`), reaproveitando `WeatherToolResult` como shape de dado final. Este passo estabelece o cenário multi-tile que hoje não existe no projeto (pré-requisito prático pros passos seguintes, já que hoje só existe 1 card fixo).

- **Issue:** [#78 — `[Back] -GOOGLE-A2UI- Define a compact weather dashboard DSL instead of full A2UI markup`](https://github.com/doljak-projects/A2UI_A17_Python/issues/78)

### Passo 2 — Conversão determinística DSL → A2UI no backend
Implementar, em código Python puro (sem LLM), a conversão da DSL do Passo 1 numa mensagem `updateComponents` real (reaproveitando o padrão de árvore achatada já usado em `createWeatherCard()` — `Card`/`Column`/`Text`, um bloco por tile pedido). O LLM só decide a DSL; a estrutura A2UI é sempre gerada por código determinístico.

- **Issue:** [#79 — `[Back] -GOOGLE-A2UI- Deterministic DSL-to-A2UI conversion in the backend`](https://github.com/doljak-projects/A2UI_A17_Python/issues/79)

### Passo 3 — Cache de estrutura por hash da requisição
Cachear a DSL (e a estrutura `updateComponents` derivada dela) usando um hash da descrição/parâmetros da requisição como chave. Em cache-hit, pular a geração da DSL (e portanto o LLM) inteiramente — reenviar a estrutura cacheada + um novo `updateDataModel` com dados atualizados.

- **Issue:** [#80 — `[Back] -GOOGLE-A2UI- Cache the generated component structure by request hash`](https://github.com/doljak-projects/A2UI_A17_Python/issues/80)

## 4. O que fica para depois

O artigo discute explicitamente o trade-off da DSL: ela limita a flexibilidade generativa do LLM às opções que a própria DSL prevê (ex: não dá pra pedir uma variação de layout que a DSL não modele sem alterar o schema). Isso não é um problema a resolver nesta parte — é uma característica da técnica, documentada aqui pra quem for estender a DSL depois.
