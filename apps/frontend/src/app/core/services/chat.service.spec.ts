import { TestBed } from '@angular/core/testing';
import { ChatEvent } from '../models/chat.models';
import { ChatService } from './chat.service';

function sseResponse(frames: string[], status = 200): Response {
  const encoder = new TextEncoder();
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      for (const frame of frames) {
        controller.enqueue(encoder.encode(frame));
      }
      controller.close();
    },
  });

  return new Response(stream, {
    status,
    headers: { 'Content-Type': 'text/event-stream' },
  });
}

describe('ChatService', () => {
  let service: ChatService;
  let fetchSpy: jasmine.Spy<typeof fetch>;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ChatService);
    fetchSpy = spyOn(window, 'fetch');
  });

  it('emite deltas e done a partir de um ReadableStream mockado', (done) => {
    fetchSpy.and.resolveTo(
      sseResponse([
        'event: delta\ndata: {"text":"Ol"}\n\n',
        'event: delta\ndata: {"text":"á"}\n\n',
        'event: done\ndata: {"text":"Olá","rounds":1}\n\n',
      ]),
    );

    const events: ChatEvent[] = [];

    service.send([{ role: 'user', content: 'oi' }]).subscribe({
      next: (event) => events.push(event),
      complete: () => {
        expect(fetchSpy).toHaveBeenCalledWith(
          'http://localhost:8000/api/chat',
          jasmine.objectContaining({
            method: 'POST',
            headers: jasmine.objectContaining({
              Accept: 'text/event-stream',
            }),
            body: JSON.stringify({ messages: [{ role: 'user', content: 'oi' }] }),
          }),
        );
        expect(events).toEqual([
          { type: 'delta', text: 'Ol' },
          { type: 'delta', text: 'á' },
          { type: 'done', text: 'Olá', rounds: 1 },
        ]);
        done();
      },
      error: done.fail,
    });
  });

  it('propaga erro HTTP antes de abrir o stream', (done) => {
    fetchSpy.and.resolveTo(sseResponse([], 500));

    service.send([{ role: 'user', content: 'oi' }]).subscribe({
      next: () => done.fail('não deveria emitir eventos'),
      error: (error: Error) => {
        expect(error.message).toContain('HTTP 500');
        done();
      },
    });
  });

  it('emite evento error vindo do próprio stream SSE', (done) => {
    fetchSpy.and.resolveTo(
      sseResponse(['event: error\ndata: {"message":"provedor fora"}\n\n']),
    );

    service.send([{ role: 'user', content: 'oi' }]).subscribe({
      next: (event) => {
        expect(event).toEqual({ type: 'error', message: 'provedor fora' });
      },
      complete: done,
      error: done.fail,
    });
  });
});
