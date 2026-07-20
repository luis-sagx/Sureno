import { apiFetch } from '@/lib/csrf';

interface DeleteDialogOptions {
  dialogId: string;
  endpoint: (id: string) => string;
  fallbackName: string;
  errorMessage: string;
}

export function bindDeleteDialog(options: DeleteDialogOptions): void {
  const dialog = document.getElementById(options.dialogId) as HTMLDialogElement | null;
  if (!dialog) return;

  const selectedName = dialog.querySelector<HTMLElement>('[data-delete-name]');
  let selectedId = '';

  document.querySelectorAll<HTMLButtonElement>('[data-del]').forEach((button) => {
    button.addEventListener('click', () => {
      selectedId = button.dataset.del ?? '';
      if (selectedName) selectedName.textContent = button.dataset.delName || options.fallbackName;
      dialog.showModal();
    });
  });

  dialog.querySelector('[data-delete-cancel]')?.addEventListener('click', () => dialog.close());
  dialog.querySelector('[data-delete-confirm]')?.addEventListener('click', async () => {
    if (!selectedId) return;
    const response = await apiFetch(options.endpoint(selectedId), { method: 'DELETE' });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      alert(data.error || options.errorMessage);
      return;
    }
    document.querySelector(`[data-row="${selectedId}"]`)?.remove();
    selectedId = '';
    dialog.close();
  });
}
