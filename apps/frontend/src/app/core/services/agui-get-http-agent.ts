import { HttpAgent, RunAgentInput } from '@ag-ui/client';

/**
 * `HttpAgent` sempre monta `POST` com o `RunAgentInput` inteiro no corpo
 * (ver `requestInit()` no SDK). Nossas rotas AG-UI (`GET /api/agui/*`) não
 * recebem corpo, então este override troca só o método/headers da request.
 */
export class AguiGetHttpAgent extends HttpAgent {
  protected override requestInit(_input: RunAgentInput): RequestInit {
    return {
      method: 'GET',
      headers: { ...this.headers, Accept: 'text/event-stream' },
      signal: this.abortController.signal,
    };
  }
}
