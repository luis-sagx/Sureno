// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from 'vitest';

const apiFetch = vi.fn();
vi.mock('@/lib/csrf', () => ({ apiFetch: (...args: unknown[]) => apiFetch(...args) }));

const { bindDeleteDialog } = await import('@/lib/delete-dialog');

const options = {
  dialogId: 'dlg',
  endpoint: (id: string) => `/api/products/${id}`,
  fallbackName: 'este producto',
  errorMessage: 'No se pudo eliminar el producto',
};

/** jsdom no implementa showModal/close: se instrumentan para poder observarlos. */
function renderDialog(): { dialog: HTMLDialogElement; showModal: ReturnType<typeof vi.fn>; close: ReturnType<typeof vi.fn> } {
  document.body.innerHTML = `
    <button data-del="p1" data-del-name="Ron Sureño">Eliminar</button>
    <button data-del="p2">Eliminar</button>
    <table><tbody><tr data-row="p1"><td>Ron Sureño</td></tr></tbody></table>
    <dialog id="dlg">
      <span data-delete-name></span>
      <button data-delete-cancel>Cancelar</button>
      <button data-delete-confirm>Confirmar</button>
    </dialog>`;
  const dialog = document.getElementById('dlg') as HTMLDialogElement;
  const showModal = vi.fn();
  const close = vi.fn();
  dialog.showModal = showModal;
  dialog.close = close;
  return { dialog, showModal, close };
}

const click = (selector: string) => document.querySelector<HTMLElement>(selector)!.click();
const flush = () => new Promise((resolve) => setTimeout(resolve, 0));

describe('bindDeleteDialog', () => {
  beforeEach(() => {
    apiFetch.mockReset();
    vi.restoreAllMocks();
  });

  it('does nothing when the dialog is not present', () => {
    document.body.innerHTML = '<button data-del="p1"></button>';
    expect(() => bindDeleteDialog(options)).not.toThrow();
  });

  it('opens the dialog with the product name of the clicked row', () => {
    const { showModal } = renderDialog();
    bindDeleteDialog(options);

    click('[data-del="p1"]');

    expect(showModal).toHaveBeenCalledOnce();
    expect(document.querySelector('[data-delete-name]')!.textContent).toBe('Ron Sureño');
  });

  it('falls back to the generic name when the row has no data-del-name', () => {
    renderDialog();
    bindDeleteDialog(options);

    click('[data-del="p2"]');

    expect(document.querySelector('[data-delete-name]')!.textContent).toBe('este producto');
  });

  it('closes the dialog on cancel without calling the API', () => {
    const { close } = renderDialog();
    bindDeleteDialog(options);

    click('[data-del="p1"]');
    click('[data-delete-cancel]');

    expect(close).toHaveBeenCalledOnce();
    expect(apiFetch).not.toHaveBeenCalled();
  });

  it('ignores the confirmation when no row was selected', async () => {
    renderDialog();
    bindDeleteDialog(options);

    click('[data-delete-confirm]');
    await flush();

    expect(apiFetch).not.toHaveBeenCalled();
  });

  it('deletes the row and closes the dialog on a successful response', async () => {
    const { close } = renderDialog();
    apiFetch.mockResolvedValue({ ok: true, json: async () => ({}) });
    bindDeleteDialog(options);

    click('[data-del="p1"]');
    click('[data-delete-confirm]');
    await flush();

    expect(apiFetch).toHaveBeenCalledWith('/api/products/p1', { method: 'DELETE' });
    expect(document.querySelector('[data-row="p1"]')).toBeNull();
    expect(close).toHaveBeenCalledOnce();
  });

  it('alerts the API error and keeps the row when the deletion fails', async () => {
    const { close } = renderDialog();
    const alert = vi.spyOn(window, 'alert').mockImplementation(() => {});
    apiFetch.mockResolvedValue({ ok: false, json: async () => ({ error: 'Producto en un pedido' }) });
    bindDeleteDialog(options);

    click('[data-del="p1"]');
    click('[data-delete-confirm]');
    await flush();

    expect(alert).toHaveBeenCalledWith('Producto en un pedido');
    expect(document.querySelector('[data-row="p1"]')).not.toBeNull();
    expect(close).not.toHaveBeenCalled();
  });

  it('alerts the default message when the failed response has no JSON body', async () => {
    renderDialog();
    const alert = vi.spyOn(window, 'alert').mockImplementation(() => {});
    apiFetch.mockResolvedValue({
      ok: false,
      json: async () => {
        throw new Error('not json');
      },
    });
    bindDeleteDialog(options);

    click('[data-del="p1"]');
    click('[data-delete-confirm]');
    await flush();

    expect(alert).toHaveBeenCalledWith(options.errorMessage);
  });
});
