from __future__ import annotations

import json
from abc import ABC, abstractmethod
from collections.abc import Iterator

from ag_ui.core import (
    ActivitySnapshotEvent,
    BaseEvent,
    RunAgentInput,
    RunFinishedEvent,
    RunStartedEvent,
    TextMessageContentEvent,
    TextMessageEndEvent,
    TextMessageStartEvent,
    ToolCallArgsEvent,
    ToolCallEndEvent,
    ToolCallResultEvent,
    ToolCallStartEvent,
    ToolMessage,
)

from app.agui.a2ui_constants import (
    A2UI_SURFACE_ACTIVITY_TYPE,
    MCP_APPS_ACTIVITY_TYPE,
    WEATHER_CATALOG_ID,
    WEATHER_MCP_RESOURCE_URI,
    WEATHER_MCP_SERVER_HASH,
)
from app.agui.a2ui_weather_card import create_weather_card
from app.agui.dashboard_cache import dashboard_structure_cache
from app.agui.dashboard_dsl import build_dashboard_data_model, dsl_from_cities, hash_dsl
from app.agui.mcp_proxy import McpProxyError, execute_proxied_mcp_request
from app.services.weather import get_weather


class AGUIAgent(ABC):
    """Equivalente Python ao `AbstractAgent` do SDK TypeScript do AG-UI.

    O SDK TS expõe `run(input): Observable<BaseEvent>`; aqui o stream reativo
    vira um generator síncrono, mesmo padrão já usado em `app/llm/streaming.py`.
    """

    @abstractmethod
    def run(self, input: RunAgentInput) -> Iterator[BaseEvent]:
        raise NotImplementedError

    def _proxy_mcp_request_events(self, input: RunAgentInput) -> Iterator[BaseEvent]:
        """Atende requisições MCP Apps proxied pelo CopilotKit (issue #85).

        O `MCPAppsMiddleware`-equivalente deste projeto não existe no lado
        transporte HTTP — o proxy acontece aqui, dentro do próprio agente:
        quando o widget (dentro do iframe) pede um recurso/tool via
        `provideMCPApps`, o CopilotKit encaminha a requisição pro agente ativo
        via `forwarded_props.__proxiedMCPRequest`, em vez de bater direto no
        MCP Server.
        """
        proxy_request = input.forwarded_props.get("__proxiedMCPRequest")
        if proxy_request is None:
            return

        yield RunStartedEvent(thread_id=input.thread_id, run_id=input.run_id)
        try:
            result = execute_proxied_mcp_request(proxy_request)
        except McpProxyError as exc:
            yield RunFinishedEvent(
                thread_id=input.thread_id,
                run_id=input.run_id,
                result={"isError": True, "content": [{"type": "text", "text": str(exc)}]},
            )
            return

        yield RunFinishedEvent(
            thread_id=input.thread_id,
            run_id=input.run_id,
            result=result,
        )


class WeatherChatAgent(AGUIAgent):
    """Equivalente Python ao `FlightWeatherAgent` do artigo, sem chamar o LLM.

    Emite apenas a sequência mínima de um turno de conversa
    (RUN_STARTED -> TEXT_MESSAGE_* -> RUN_FINISHED) para validar o formato
    AG-UI, como no tutorial original.
    """

    MESSAGE_ID = "1001"

    def run(self, input: RunAgentInput) -> Iterator[BaseEvent]:
        yield RunStartedEvent(thread_id=input.thread_id, run_id=input.run_id)

        yield TextMessageStartEvent(message_id=self.MESSAGE_ID, role="assistant")
        for delta in self._reply_deltas():
            yield TextMessageContentEvent(message_id=self.MESSAGE_ID, delta=delta)
        yield TextMessageEndEvent(message_id=self.MESSAGE_ID)

        yield RunFinishedEvent(thread_id=input.thread_id, run_id=input.run_id)

    def _reply_deltas(self) -> Iterator[str]:
        yield "Consultando o clima para São Paulo..."


class WeatherClientToolCallAgent(AGUIAgent):
    """Demo da issue #36: pede uma tool call **client-side**, sem resolver.

    Ao contrário do `WeatherToolCallAgent` (#33, server-side), este agente
    para no `TOOL_CALL_END` — não chama `get_weather` nem emite
    `TOOL_CALL_RESULT`. A tool call fica pendente para o cliente detectar
    (via `AgentSubscriber`), executar a ação local e devolver o resultado
    numa segunda run.
    """

    TOOL_CALL_ID = "4001"
    CITY = "São Paulo"

    def run(self, input: RunAgentInput) -> Iterator[BaseEvent]:
        yield RunStartedEvent(thread_id=input.thread_id, run_id=input.run_id)

        yield ToolCallStartEvent(tool_call_id=self.TOOL_CALL_ID, tool_call_name="show_weather")
        yield ToolCallArgsEvent(
            tool_call_id=self.TOOL_CALL_ID,
            delta=json.dumps({"city": self.CITY}, ensure_ascii=False),
        )
        yield ToolCallEndEvent(tool_call_id=self.TOOL_CALL_ID)

        yield RunFinishedEvent(thread_id=input.thread_id, run_id=input.run_id)


class WeatherResumableToolCallAgent(AGUIAgent):
    """Demo da issue #45: recebe um `RunAgentInput` real via POST (com corpo),
    ao contrário das demos GET (#32/#33/#36). Ainda sem a lógica de
    ramificação (Passo 2+) — por enquanto só valida que o corpo real chega
    até aqui.
    """

    TOOL_CALL_ID = "5001"
    MESSAGE_ID = "5002"
    CITY = "São Paulo"

    def run(self, input: RunAgentInput) -> Iterator[BaseEvent]:
        yield RunStartedEvent(thread_id=input.thread_id, run_id=input.run_id)

        tool_result = self._find_tool_result(input)
        if tool_result is None:
            yield from self._request_tool_call()
        else:
            yield from self._acknowledge_tool_result(tool_result)

        yield RunFinishedEvent(thread_id=input.thread_id, run_id=input.run_id)

    def _request_tool_call(self) -> Iterator[BaseEvent]:
        yield ToolCallStartEvent(tool_call_id=self.TOOL_CALL_ID, tool_call_name="show_weather")
        yield ToolCallArgsEvent(
            tool_call_id=self.TOOL_CALL_ID,
            delta=json.dumps({"city": self.CITY}, ensure_ascii=False),
        )
        yield ToolCallEndEvent(tool_call_id=self.TOOL_CALL_ID)

    def _acknowledge_tool_result(self, tool_result: ToolMessage) -> Iterator[BaseEvent]:
        weather = json.loads(tool_result.content)
        reply = (
            f"Recebi o clima de {weather['city']}: {weather['temperature_c']}°C, "
            f"{weather['description']}, umidade {weather['humidity']}%."
        )

        yield TextMessageStartEvent(message_id=self.MESSAGE_ID, role="assistant")
        yield TextMessageContentEvent(message_id=self.MESSAGE_ID, delta=reply)
        yield TextMessageEndEvent(message_id=self.MESSAGE_ID)

    def _find_tool_result(self, input: RunAgentInput) -> ToolMessage | None:
        """Backend é stateless entre requisições — a única forma de saber se
        o cliente já resolveu a tool call é procurar, no `messages` que ele
        reenviou, uma `ToolMessage` respondendo ao `TOOL_CALL_ID` desta
        instância.
        """
        for message in input.messages:
            if isinstance(message, ToolMessage) and message.tool_call_id == self.TOOL_CALL_ID:
                return message
        return None


class WeatherToolCallAgent(AGUIAgent):
    """Estende o esqueleto da issue #32 com uma tool call server-side real.

    Equivalente ao passo "Tool Call no Servidor" do artigo: em vez de mockar o
    resultado, reaproveita a tool `get_weather` já existente no backend (#5).
    """

    TOOL_CALL_ID = "2001"
    MESSAGE_ID = "3001"
    CITY = "São Paulo"

    def run(self, input: RunAgentInput) -> Iterator[BaseEvent]:
        yield RunStartedEvent(thread_id=input.thread_id, run_id=input.run_id)

        yield ToolCallStartEvent(tool_call_id=self.TOOL_CALL_ID, tool_call_name="get_weather")
        yield ToolCallArgsEvent(
            tool_call_id=self.TOOL_CALL_ID,
            delta=json.dumps({"city": self.CITY}, ensure_ascii=False),
        )
        yield ToolCallEndEvent(tool_call_id=self.TOOL_CALL_ID)

        result = get_weather(self.CITY)

        yield ToolCallResultEvent(
            message_id=self.MESSAGE_ID,
            tool_call_id=self.TOOL_CALL_ID,
            content=result.model_dump_json(),
            role="tool",
        )

        yield RunFinishedEvent(thread_id=input.thread_id, run_id=input.run_id)


class WeatherA2UiActivityAgent(AGUIAgent):
    """Issue #72: emite operações A2UI dentro de um ACTIVITY_SNAPSHOT.

    Reaproveita o mesmo ciclo `createSurface`/`updateComponents`/`updateDataModel`
    já usado na rota de demo isolada `/a2ui-test` (issues #53/#54), mas agora
    emitido por um agente real via transporte AG-UI — em vez do cliente montar
    as mensagens manualmente.
    """

    ACTIVITY_MESSAGE_ID = "6001"
    SURFACE_ID = "weather-chat-surface"
    CITY = "São Paulo"

    def run(self, input: RunAgentInput) -> Iterator[BaseEvent]:
        weather = get_weather(self.CITY)
        operations = create_weather_card(
            self.SURFACE_ID, WEATHER_CATALOG_ID, weather, use_humidity_gauge=True
        )

        yield RunStartedEvent(thread_id=input.thread_id, run_id=input.run_id)
        yield ActivitySnapshotEvent(
            message_id=self.ACTIVITY_MESSAGE_ID,
            activity_type=A2UI_SURFACE_ACTIVITY_TYPE,
            content={"operations": operations},
        )
        yield RunFinishedEvent(thread_id=input.thread_id, run_id=input.run_id)


class WeatherDashboardActivityAgent(AGUIAgent):
    """Issues #78-#80: DSL compacta + conversão determinística + cache.

    O agente só decide a DSL (`dsl_from_cities`) — a estrutura A2UI
    (`updateComponents`) é sempre gerada por código determinístico
    (`dashboard_structure_cache`), nunca pelo LLM. Em cache-hit, a estrutura
    é reaproveitada e só o `updateDataModel` é reconstruído com dados frescos.
    """

    ACTIVITY_MESSAGE_ID = "7001"
    SURFACE_ID = "weather-dashboard-surface"
    DEFAULT_CITIES = ("São Paulo", "Rio de Janeiro", "Curitiba")

    def run(self, input: RunAgentInput) -> Iterator[BaseEvent]:
        dsl = dsl_from_cities(list(self.DEFAULT_CITIES))
        request_hash = hash_dsl(dsl)
        cached = dashboard_structure_cache.get(request_hash)
        cache_hit = cached is not None
        if cached is None:
            cached = dashboard_structure_cache.put(request_hash, dsl, self.SURFACE_ID)

        weather_by_tile = [get_weather(tile.city) for tile in cached.dsl.tiles]
        operations = [
            {
                "version": "v0.9",
                "createSurface": {
                    "surfaceId": self.SURFACE_ID,
                    "catalogId": WEATHER_CATALOG_ID,
                },
            },
            {
                "version": "v0.9",
                "updateComponents": {
                    "surfaceId": self.SURFACE_ID,
                    "components": cached.components,
                },
            },
            {
                "version": "v0.9",
                "updateDataModel": {
                    "surfaceId": self.SURFACE_ID,
                    "value": build_dashboard_data_model(weather_by_tile),
                },
            },
        ]

        yield RunStartedEvent(thread_id=input.thread_id, run_id=input.run_id)
        yield ActivitySnapshotEvent(
            message_id=self.ACTIVITY_MESSAGE_ID,
            activity_type=A2UI_SURFACE_ACTIVITY_TYPE,
            content={"operations": operations, "cacheHit": cache_hit},
        )
        yield RunFinishedEvent(thread_id=input.thread_id, run_id=input.run_id)


class WeatherMcpAppsActivityAgent(AGUIAgent):
    """Issues #84/#85: snapshot mcp-apps + proxy de recurso/tool.

    Mesmo transporte `ACTIVITY_SNAPSHOT` já usado pelo A2UI (issue #72), mas
    carregando metadata de MCP Apps (`resourceUri` + resultado estruturado da
    tool) em vez de operações A2UI. Quando o widget (dentro do iframe) precisa
    buscar o recurso/tool de novo via `provideMCPApps`, a requisição chega
    proxied em `forwarded_props.__proxiedMCPRequest` e é resolvida por
    `_proxy_mcp_request_events` (herdado de `AGUIAgent`).
    """

    ACTIVITY_MESSAGE_ID = "8001"
    CITY = "São Paulo"

    def run(self, input: RunAgentInput) -> Iterator[BaseEvent]:
        if input.forwarded_props.get("__proxiedMCPRequest"):
            yield from self._proxy_mcp_request_events(input)
            return

        weather = get_weather(self.CITY)
        weather_payload = json.loads(weather.model_dump_json())

        yield RunStartedEvent(thread_id=input.thread_id, run_id=input.run_id)
        yield ActivitySnapshotEvent(
            message_id=self.ACTIVITY_MESSAGE_ID,
            activity_type=MCP_APPS_ACTIVITY_TYPE,
            content={
                "serverHash": WEATHER_MCP_SERVER_HASH,
                "resourceUri": WEATHER_MCP_RESOURCE_URI,
                "toolInput": {"city": self.CITY},
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(weather_payload, ensure_ascii=False),
                        }
                    ],
                    "structuredContent": weather_payload,
                },
            },
        )
        yield RunFinishedEvent(thread_id=input.thread_id, run_id=input.run_id)
