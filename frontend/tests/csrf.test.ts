// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { apiFetch } from '@/lib/csrf';

describe('apiFetch', () => {
  beforeEach(() => {
    document.cookie = 'csrf_token=; Max-Age=0; path=/';
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(null, { status: 204 })));
  });

  it('sends safe methods without requesting a CSRF token', async () => {
    await apiFetch('/api/products');

    expect(fetch).toHaveBeenCalledOnce();
    expect(fetch).toHaveBeenCalledWith('/api/products', expect.objectContaining({
      credentials: 'same-origin',
    }));
  });

  it('adds the cookie token to mutating requests', async () => {
    document.cookie = 'csrf_token=token%20value; path=/';
    await apiFetch('/api/orders', { method: 'POST', body: '{}' });

    const init = vi.mocked(fetch).mock.calls[0][1]!;
    const headers = init.headers as Headers;
    expect(headers.get('X-CSRFToken')).toBe('token value');
    expect(headers.get('Content-Type')).toBe('application/json');
  });

  it('obtains a token before a mutating request when the cookie is absent', async () => {
    vi.mocked(fetch).mockImplementation(async (input) => {
      if (input === '/api/csrf') document.cookie = 'csrf_token=seeded; path=/';
      return new Response(null, { status: 204 });
    });

    await apiFetch('/api/logout', { method: 'POST' });

    expect(fetch).toHaveBeenNthCalledWith(1, '/api/csrf', { credentials: 'same-origin' });
    const headers = vi.mocked(fetch).mock.calls[1][1]!.headers as Headers;
    expect(headers.get('X-CSRFToken')).toBe('seeded');
  });

  it('does not set a JSON content type for FormData', async () => {
    document.cookie = 'csrf_token=token; path=/';
    await apiFetch('/api/products', { method: 'POST', body: new FormData() });

    const headers = vi.mocked(fetch).mock.calls[0][1]!.headers as Headers;
    expect(headers.has('Content-Type')).toBe(false);
  });

  it('preserves caller headers and credentials', async () => {
    await apiFetch('/api/products', { headers: { Accept: 'application/problem+json' } });
    const init = vi.mocked(fetch).mock.calls[0][1]!;

    expect((init.headers as Headers).get('Accept')).toBe('application/problem+json');
    expect(init.credentials).toBe('same-origin');
  });
});
