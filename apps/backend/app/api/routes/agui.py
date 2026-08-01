from __future__ import annotations

import uuid
from collections.abc import Iterator

from ag_ui.core import RunAgentInput, RunErrorEvent
from ag_ui.encoder import EventEncoder
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.agui.agent import (
    AGUIAgent,
    WeatherChatAgent,
    WeatherClientToolCallAgent,
    WeatherResumableToolCallAgent,
    WeatherToolCallAgent,
)

router = APIRouter()

# Mesmos headers do endpoint /api/chat (app/api/routes/chat.py): sem eles o
# proxy/nginx pode segurar o buffer e o cliente recebe tudo de uma vez.
SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


@router.get("/agui/demo")
def agui_demo() -> StreamingResponse:
    """Demo funcional da issue #32: roda o `WeatherChatAgent` e transmite os
    eventos AG-UI reais via SSE, sem chamar nenhum LLM.
    """
    return _stream(WeatherChatAgent())


@router.get("/agui/weather-tool-demo")
def agui_weather_tool_demo() -> StreamingResponse:
    """Demo funcional da issue #33: roda o `WeatherToolCallAgent`, que emite uma
    tool call server-side e a resolve com o `get_weather` real (issue #5).
    """
    return _stream(WeatherToolCallAgent())


@router.get("/agui/weather-tool-client-demo")
def agui_weather_tool_client_demo() -> StreamingResponse:
    """Demo funcional da issue #36: roda o `WeatherClientToolCallAgent`, que
    emite uma tool call pendente para o cliente resolver (sem `TOOL_CALL_RESULT`).
    """
    return _stream(WeatherClientToolCallAgent())


@router.post("/agui/weather-tool-agent-demo")
def agui_weather_tool_agent_demo(run_input: RunAgentInput) -> StreamingResponse:
    """Demo funcional da issue #45: primeira rota AG-UI com corpo real (POST),
    ao contrário das demos GET (#32/#33/#36) que sempre montam um
    `RunAgentInput` vazio internamente. `RunAgentInput` já é um modelo
    Pydantic (`ag_ui.core`), então o FastAPI valida/parseia o corpo sozinho.
    """
    return _stream(WeatherResumableToolCallAgent(), run_input)


def _stream(agent: AGUIAgent, run_input: RunAgentInput | None = None) -> StreamingResponse:
    return StreamingResponse(
        _event_stream(agent, run_input),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )


def _event_stream(agent: AGUIAgent, run_input: RunAgentInput | None) -> Iterator[str]:
    if run_input is None:
        run_input = RunAgentInput(
            thread_id=str(uuid.uuid4()),
            run_id=str(uuid.uuid4()),
            state=None,
            messages=[],
            tools=[],
            context=[],
            forwarded_props={},
        )
    encoder = EventEncoder()

    try:
        for event in agent.run(run_input):
            yield encoder.encode(event)
    except Exception as exc:
        # A resposta já começou com 200, então a falha precisa viajar como evento
        # (mesma estratégia de app/api/routes/chat.py, adaptada ao AG-UI).
        yield encoder.encode(RunErrorEvent(message=str(exc)))
