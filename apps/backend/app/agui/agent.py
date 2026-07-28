from __future__ import annotations

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
)


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
