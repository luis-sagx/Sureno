import { apiFetch } from '@/lib/csrf';

interface JsonFormOptions {
  formId: string;
  endpoint: string;
  defaultRedirect: string;
  errorMessage: string;
}

export function bindJsonForm(options: JsonFormOptions): void {
  const form = document.getElementById(options.formId) as HTMLFormElement | null;
  const errorBox = document.querySelector<HTMLElement>('[data-error]');
  if (!form) return;

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    errorBox?.classList.add('hidden');
    const button = form.querySelector<HTMLButtonElement>('button[type=submit]');
    if (button) button.disabled = true;
    try {
      const body = Object.fromEntries(new FormData(form).entries());
      const response = await apiFetch(options.endpoint, { method: 'POST', body: JSON.stringify(body) });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.error || options.errorMessage);
      window.location.href = data.redirect || options.defaultRedirect;
    } catch (error) {
      if (errorBox) {
        errorBox.textContent = error instanceof Error ? error.message : 'Error de conexión con el servidor';
        errorBox.classList.remove('hidden');
      }
    } finally {
      if (button) button.disabled = false;
    }
  });
}
