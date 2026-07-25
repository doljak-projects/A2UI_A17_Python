import { TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';
import { routes } from './app.routes';

describe('app.routes', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideRouter(routes)],
    });
  });

  it('redireciona a raiz para /chat', async () => {
    const router = TestBed.inject(Router);
    await router.navigateByUrl('/');
    expect(router.url).toBe('/chat');
  });

  it('carrega a rota /home', async () => {
    const router = TestBed.inject(Router);
    await router.navigateByUrl('/home');
    expect(router.url).toBe('/home');
  });

  it('redireciona rotas desconhecidas para /chat', async () => {
    const router = TestBed.inject(Router);
    await router.navigateByUrl('/rota-inexistente');
    expect(router.url).toBe('/chat');
  });
});
