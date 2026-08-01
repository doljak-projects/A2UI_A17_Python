import { RunAgentInput } from '@ag-ui/client';

import { AguiGetHttpAgent } from './agui-get-http-agent';

describe('AguiGetHttpAgent', () => {
  it('monta a requisição como GET, sem corpo, mantendo o Accept de SSE', () => {
    const agent = new AguiGetHttpAgent({
      url: 'http://localhost:8000/api/agui/weather-tool-demo',
    });

    const init = (agent as unknown as { requestInit(input: RunAgentInput): RequestInit }).requestInit(
      {} as RunAgentInput,
    );

    expect(init.method).toBe('GET');
    expect(init.body).toBeUndefined();
    expect(init.headers).toEqual(jasmine.objectContaining({ Accept: 'text/event-stream' }));
    expect(init.signal).toBe(agent.abortController.signal);
  });
});
