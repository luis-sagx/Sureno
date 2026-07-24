// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from 'vitest';

const apiFetch = vi.fn();
vi.mock('@/lib/csrf', () => ({ apiFetch: (...args: unknown[]) => apiFetch(...args) }));

const { bindJsonForm } = await import('@/lib/json-form');

const options = {
  formId: 'login-form',
  endpoint: '/api/login',
  defaultRedirect: '/index',
  errorMessage: 'Credenciales invalidas',
};

function renderForm(): void {
  document.body.innerHTML = `
    <p data-error class="hidden"></p>
    <form id="login-form">
      <input name="email" value="cliente@test.com" />
      <input name="password" value="ingreso1" />
      <button type="submit">Entrar</button>
    </form>`;
}

const submit = () => document.querySelector('form')!.dispatchEvent(new Event('submit', { cancelable: true }));
const flush = () => new Promise((resolve) => setTimeout(resolve, 0));
const errorBox = () => document.querySelector<HTMLElement>('[data-error]')!;
const button = () => document.querySelector<HTMLButtonElement>('button[type=submit]')!;

describe('bindJsonForm', () => {
  beforeEach(() => {
    apiFetch.mockReset();
    renderForm();
    // window.location.href no es asignable en jsdom sin redefinirlo.
    Object.defineProperty(window, 'location', { value: { href: '' }, writable: true });
  });

  it('does nothing when the form is not present', () => {
    document.body.innerHTML = '';
    expect(() => bindJsonForm(options)).not.toThrow();
  });

  it('serializes the form as JSON and redirects to the server-provided URL', async () => {
    apiFetch.mockResolvedValue({ ok: true, json: async () => ({ redirect: '/admin/home' }) });
    bindJsonForm(options);

    submit();
    await flush();

    expect(apiFetch).toHaveBeenCalledWith('/api/login', {
      method: 'POST',
      body: JSON.stringify({ email: 'cliente@test.com', password: 'ingreso1' }),
    });
    expect(window.location.href).toBe('/admin/home');
    expect(button().disabled).toBe(false);
  });

  it('falls back to the default redirect when the response has no redirect', async () => {
    apiFetch.mockResolvedValue({ ok: true, json: async () => ({}) });
    bindJsonForm(options);

    submit();
    await flush();

    expect(window.location.href).toBe('/index');
  });

  it('shows the API error message and re-enables the button', async () => {
    apiFetch.mockResolvedValue({ ok: false, json: async () => ({ error: 'Email ya registrado' }) });
    bindJsonForm(options);

    submit();
    await flush();

    expect(errorBox().textContent).toBe('Email ya registrado');
    expect(errorBox().classList.contains('hidden')).toBe(false);
    expect(button().disabled).toBe(false);
    expect(window.location.href).toBe('');
  });

  it('shows the default message when the failed response has no JSON body', async () => {
    apiFetch.mockResolvedValue({
      ok: false,
      json: async () => {
        throw new Error('not json');
      },
    });
    bindJsonForm(options);

    submit();
    await flush();

    expect(errorBox().textContent).toBe(options.errorMessage);
  });

  it('reports a connection error when the request itself rejects', async () => {
    apiFetch.mockRejectedValue('network down');
    bindJsonForm(options);

    submit();
    await flush();

    expect(errorBox().textContent).toBe('Error de conexión con el servidor');
  });

  it('works when neither the error box nor the submit button exist', async () => {
    document.body.innerHTML = '<form id="login-form"><input name="email" value="a@b.c" /></form>';
    apiFetch.mockResolvedValue({ ok: false, json: async () => ({}) });
    bindJsonForm(options);

    submit();
    await flush();

    expect(apiFetch).toHaveBeenCalledOnce();
  });
});
