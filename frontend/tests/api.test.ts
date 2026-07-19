import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiServer, getSessionUser } from '@/lib/api';

describe('apiServer', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('forwards cookies and parses a successful JSON response', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(
      JSON.stringify({ id: 1 }),
      { status: 200, headers: { 'Content-Type': 'application/json' } },
    )));
    const request = new Request('http://astro.local/products', {
      headers: { cookie: 'session=abc' },
    });

    await expect(apiServer('/api/products', request)).resolves.toEqual({
      ok: true,
      status: 200,
      data: { id: 1 },
      error: undefined,
    });
    expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/products', expect.objectContaining({
      headers: expect.objectContaining({ cookie: 'session=abc' }),
    }));
  });

  it('normalizes paths and adds JSON content type for request bodies', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(null, { status: 204 })));
    await apiServer('api/orders', new Request('http://astro.local'), {
      method: 'POST',
      body: '{}',
    });

    expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/orders', expect.objectContaining({
      headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
    }));
  });

  it('returns the backend error message on HTTP failures', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(
      JSON.stringify({ error: 'No autorizado' }),
      { status: 401, statusText: 'Unauthorized' },
    )));

    await expect(apiServer('/api/user', new Request('http://astro.local'))).resolves.toEqual({
      ok: false,
      status: 401,
      data: { error: 'No autorizado' },
      error: 'No autorizado',
    });
  });

  it('handles non-JSON responses and network failures', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response('not-json', { status: 502, statusText: 'Bad Gateway' }))
      .mockRejectedValueOnce(new Error('offline'));
    vi.stubGlobal('fetch', fetchMock);

    await expect(apiServer('/api/user', new Request('http://astro.local'))).resolves.toEqual({
      ok: false, status: 502, data: null, error: 'Bad Gateway',
    });
    await expect(apiServer('/api/user', new Request('http://astro.local'))).resolves.toMatchObject({
      ok: false, status: 0, data: null, error: 'Error: offline',
    });
  });

  it('returns only authenticated session users', async () => {
    vi.stubGlobal('fetch', vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({ email: 'admin@sureno.ec', nombre: 'Ana' })))
      .mockResolvedValueOnce(new Response(JSON.stringify({ error: 'No autorizado' }), { status: 401 })));
    const request = new Request('http://astro.local');

    await expect(getSessionUser(request)).resolves.toEqual({ email: 'admin@sureno.ec', nombre: 'Ana' });
    await expect(getSessionUser(request)).resolves.toBeNull();
  });
});
