# Backend AG-UI (issues #32, #33) — como o agente Python funciona

> Arquitetura da implementação Python do protocolo AG-UI, decidida na issue #32
> em vez de replicar o SDK TypeScript do artigo original — ver
> [`32-Back-ag-ui-agent-skeleton.md`](../issues-plans/32-Back-ag-ui-agent-skeleton.md)
> para a justificativa completa.

## Hierarquia de classes

`AGUIAgent` é o equivalente Python ao `AbstractAgent` do SDK TypeScript: uma
classe abstrata com um único método, `run()`, que devolve um generator
síncrono de eventos AG-UI (`Iterator[BaseEvent]`) em vez de um
`Observable<BaseEvent>` do RxJS.

```mermaid
classDiagram
    class AGUIAgent {
        <<abstract>>
        +run(input: RunAgentInput) Iterator~BaseEvent~
    }
    class WeatherChatAgent {
        +MESSAGE_ID
        +run(input) Iterator~BaseEvent~
        emite RUN_STARTED → TEXT_MESSAGE_* → RUN_FINISHED
    }
    class WeatherToolCallAgent {
        +TOOL_CALL_ID
        +MESSAGE_ID
        +CITY
        +run(input) Iterator~BaseEvent~
        emite RUN_STARTED → TOOL_CALL_* → RUN_FINISHED
    }
    AGUIAgent <|-- WeatherChatAgent
    AGUIAgent <|-- WeatherToolCallAgent
    WeatherToolCallAgent ..> get_weather : chama (issue #5)
```

## Da requisição HTTP ao SSE

```mermaid
flowchart LR
    subgraph Rotas["app/api/routes/agui.py"]
        R1["GET /api/agui/demo"]
        R2["GET /api/agui/weather-tool-demo"]
    end
    subgraph Agentes["app/agui/agent.py"]
        A1["WeatherChatAgent"]
        A2["WeatherToolCallAgent"]
    end
    W["get_weather()<br/>app/services/weather.py"]
    ENC["EventEncoder<br/>ag_ui.encoder"]
    ERR["RunErrorEvent<br/>(RUN_ERROR)"]
    SSE["StreamingResponse<br/>text/event-stream"]

    R1 --> A1
    R2 --> A2
    A2 -->|sucesso| W
    A2 -.->|exceção do get_weather| ERR
    A1 --> ENC
    A2 --> ENC
    ERR --> ENC
    ENC --> SSE
```

O tratamento de erro (`RunErrorEvent`/`RUN_ERROR`) foi adicionado na issue #33
depois de observar, testando manualmente sem uma `WEATHER_API_KEY` válida, que
o stream simplesmente cortava sem sinalizar falha ao cliente — ver notas em
[`33-Back-a2ui-weather-tool-call.md`](../issues-plans/33-Back-a2ui-weather-tool-call.md).

## Sequência de eventos por agente

| Agente | Rota | Sequência de eventos |
|---|---|---|
| `WeatherChatAgent` | `GET /api/agui/demo` | `RUN_STARTED` → `TEXT_MESSAGE_START` → `TEXT_MESSAGE_CONTENT` → `TEXT_MESSAGE_END` → `RUN_FINISHED` |
| `WeatherToolCallAgent` (sucesso) | `GET /api/agui/weather-tool-demo` | `RUN_STARTED` → `TOOL_CALL_START` → `TOOL_CALL_ARGS` → `TOOL_CALL_END` → `TOOL_CALL_RESULT` → `RUN_FINISHED` |
| `WeatherToolCallAgent` (falha do `get_weather`) | `GET /api/agui/weather-tool-demo` | `RUN_STARTED` → `TOOL_CALL_START` → `TOOL_CALL_ARGS` → `TOOL_CALL_END` → `RUN_ERROR` |

---
Ver também: [diagrama do frontend](34-front-agui-http-agent.md) · [doc da issue #32](../issues-plans/32-Back-ag-ui-agent-skeleton.md) · [doc da issue #33](../issues-plans/33-Back-a2ui-weather-tool-call.md)
