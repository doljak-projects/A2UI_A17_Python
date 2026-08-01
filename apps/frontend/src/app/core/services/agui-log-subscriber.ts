import { AgentSubscriber } from '@ag-ui/client';

/**
 * Handlers do escopo da issue #34: só texto/execução, sem tool call
 * (fica para os próximos passos do tutorial, #35/#36). Único objetivo aqui é
 * logar cada evento recebido para validar o transporte ponta a ponta.
 */
export const aguiLogSubscriber: AgentSubscriber = {
  onRunStartedEvent({ event }) {
    console.log('[AG-UI] RUN_STARTED', event);
  },
  onTextMessageStartEvent({ event }) {
    console.log('[AG-UI] TEXT_MESSAGE_START', event);
  },
  onTextMessageContentEvent({ event, textMessageBuffer }) {
    console.log('[AG-UI] TEXT_MESSAGE_CONTENT', event, { textMessageBuffer });
  },
  onTextMessageEndEvent({ event, textMessageBuffer }) {
    console.log('[AG-UI] TEXT_MESSAGE_END', event, { textMessageBuffer });
  },
  onRunFinishedEvent({ event }) {
    console.log('[AG-UI] RUN_FINISHED', event);
  },
};
