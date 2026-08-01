from __future__ import annotations

import json
from abc import ABC, abstractmethod
from collections.abc import Iterator

from ag_ui.core import (
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

from app.services.weather import get_weather


class AGUIAgent(ABC):
    """Equivalente Python ao `AbstractAgent` do SDK TypeScript do AG-UI.

    O SDK TS expõe `run(input): Observable<BaseEvent>`; aqui o stream reativo
    vira um generator síncrono, mesmo padrão já usado em `app/llm/streaming.py`.
    """

    @abstractmethod
    def run(self, input: RunAgentInput) -> Iterator[BaseEvent]:
        raise NotImplementedError


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
