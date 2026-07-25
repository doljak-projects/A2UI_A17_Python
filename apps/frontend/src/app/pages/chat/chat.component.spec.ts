import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideNoopAnimations } from '@angular/platform-browser/animations';
import { Observable, Subject, of, throwError } from 'rxjs';

import { ChatEvent } from '../../core/models/chat.models';
import { ChatService } from '../../core/services/chat.service';
import { ChatComponent } from './chat.component';

class ChatServiceStub {
  events: ChatEvent[] = [];
  error?: Error;

  send(): Observable<ChatEvent> {
    if (this.error) {
      return throwError(() => this.error);
    }
    return of(...this.events);
  }
}

describe('ChatComponent', () => {
  let fixture: ComponentFixture<ChatComponent>;
  let component: ChatComponent;
  let chatService: ChatServiceStub;

  beforeEach(async () => {
    chatService = new ChatServiceStub();

    await TestBed.configureTestingModule({
      imports: [ChatComponent],
      providers: [
        provideNoopAnimations(),
        { provide: ChatService, useValue: chatService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ChatComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('adiciona mensagem do usuário e acumula deltas do assistente', () => {
    chatService.events = [
      { type: 'delta', text: 'Ol' },
      { type: 'delta', text: 'á' },
      { type: 'done', text: 'Olá', rounds: 1 },
    ];

    component.userInput = 'oi';
    component.send();
    fixture.detectChanges();

    expect(component.messages()).toEqual([
      { role: 'user', content: 'oi' },
      { role: 'assistant', content: 'Olá' },
    ]);
    expect(component.isStreaming()).toBeFalse();
  });

  it('não envia mensagem vazia', () => {
    component.userInput = '   ';
    component.send();

    expect(component.messages()).toEqual([]);
  });

  it('ignora novo envio enquanto o stream está aberto', () => {
    const stream$ = new Subject<ChatEvent>();
    spyOn(chatService, 'send').and.returnValue(stream$.asObservable());

    component.userInput = 'oi';
    component.send();
    expect(component.isStreaming()).toBeTrue();

    component.userInput = 'outra';
    component.send();
    expect(component.messages().length).toBe(2);

    stream$.next({ type: 'delta', text: 'ok' });
    stream$.complete();
    expect(component.isStreaming()).toBeFalse();
  });

  it('exibe erro do stream', () => {
    chatService.events = [{ type: 'error', message: 'falhou' }];

    component.userInput = 'oi';
    component.send();
    fixture.detectChanges();

    expect(component.error()).toBe('falhou');
    expect(component.isStreaming()).toBeFalse();
  });

  it('exibe erro de rede', () => {
    chatService.error = new Error('HTTP 500');

    component.userInput = 'oi';
    component.send();
    fixture.detectChanges();

    expect(component.error()).toBe('HTTP 500');
    expect(component.isStreaming()).toBeFalse();
  });
});
