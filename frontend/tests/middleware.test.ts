import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('@/lib/api', () => ({ apiServer: vi.fn() }));

import { apiServer } from '@/lib/api';
import { onRequest } from '@/middleware';

function context(path: string, init?: RequestInit) {
  const url = new URL(path, 'http://astro.local');
  return {
    url,
    request: new Request(url, init),
    redirect: vi.fn((location: string) => Response.redirect(new URL(location, url), 302)),
  };
}

async function run(path: string, init?: RequestInit) {
  const ctx = context(path, init);
  const next = vi.fn(async () => new Response('next', { status: 200 }));
  const response = await (onRequest as any)(ctx, next);
  return { ctx, next, response };
}

describe('Astro middleware', () => {
  beforeEach(() => vi.mocked(apiServer).mockReset());

  it('proxies API requests to Flask preserving method, query and body', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('{"ok":true}', {
      status: 201,
      headers: { 'Content-Type': 'application/json' },
    })));

    const { next, response } = await run('/api/orders?detail=1', {
      method: 'POST', body: '{"items":[]}', headers: { cookie: 'session=abc' },
    });

    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:5000/api/orders?detail=1',
      expect.objectContaining({ method: 'POST', redirect: 'manual' }),
    );
    const forwarded = vi.mocked(fetch).mock.calls[0][1]!;
    expect(new TextDecoder().decode(forwarded.body as ArrayBuffer)).toBe('{"items":[]}');
    expect(response.status).toBe(201);
    expect(await response.json()).toEqual({ ok: true });
    expect(next).not.toHaveBeenCalled();
  });

  it('proxies Flask static assets without a request body', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('image', { status: 200 })));
    await run('/static/img/logo.png');
    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:5000/static/img/logo.png',
      expect.objectContaining({ method: 'GET' }),
    );
    expect(vi.mocked(fetch).mock.calls[0][1]).not.toHaveProperty('body');
  });

  it('redirects anonymous users from protected customer routes', async () => {
    vi.mocked(apiServer).mockResolvedValue({ ok: false, status: 401, data: null });
    const { ctx, next } = await run('/checkout');

    expect(apiServer).toHaveBeenCalledWith('/api/user', ctx.request);
    expect(ctx.redirect).toHaveBeenCalledWith('/login');
    expect(next).not.toHaveBeenCalled();
  });

  it('allows authenticated users into protected customer routes', async () => {
    vi.mocked(apiServer).mockResolvedValue({
      ok: true, status: 200, data: { email: 'cliente@sureno.ec', rol: 'cliente' },
    });
    const { next, response } = await run('/cart/items');
    expect(next).toHaveBeenCalledOnce();
    expect(await response.text()).toBe('next');
  });

  it('redirects non-admin users away from admin routes', async () => {
    vi.mocked(apiServer).mockResolvedValue({
      ok: true, status: 200, data: { email: 'cliente@sureno.ec', rol: 'cliente' },
    });
    const { ctx, next } = await run('/admin/products');
    expect(ctx.redirect).toHaveBeenCalledWith('/');
    expect(next).not.toHaveBeenCalled();
  });

  it('allows administrators into admin routes', async () => {
    vi.mocked(apiServer).mockResolvedValue({
      ok: true, status: 200, data: { email: 'admin@sureno.ec', rol: 'administrador' },
    });
    const { next } = await run('/admin/home');
    expect(next).toHaveBeenCalledOnce();
  });

  it('passes public routes through without querying the session', async () => {
    const { next } = await run('/products');
    expect(apiServer).not.toHaveBeenCalled();
    expect(next).toHaveBeenCalledOnce();
  });
});
