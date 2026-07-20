import { addToCart } from '@/lib/cart';

function showToast(message: string): void {
  const toast = document.querySelector<HTMLElement>('[data-toast]');
  if (!toast) return;
  toast.textContent = message;
  toast.style.opacity = '1';
  window.setTimeout(() => (toast.style.opacity = '0'), 1600);
}

export function bindAddToCartButtons(): void {
  document.querySelectorAll<HTMLButtonElement>('[data-add]').forEach((button) => {
    button.addEventListener('click', () => {
      const product = button.dataset;
      addToCart({
        id: product.id!,
        nombre: product.nombre!,
        precio: Number(product.precio),
        imagen: product.imagen!,
        mililitros: product.mililitros ? Number(product.mililitros) : undefined,
      });
      showToast(`"${product.nombre}" agregado al carrito`);
    });
  });
}
