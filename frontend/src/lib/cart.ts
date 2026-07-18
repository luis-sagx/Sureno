// Carrito en localStorage (cliente). Emite 'cart:updated' para refrescar la UI.

export interface CartItem {
  id: string;
  nombre: string;
  precio: number;
  imagen: string;
  mililitros?: number;
  cantidad: number;
}

const KEY = 'cart';

export function getCart(): CartItem[] {
  try {
    const raw = JSON.parse(localStorage.getItem(KEY) || '[]');
    return Array.isArray(raw) ? raw : [];
  } catch {
    return [];
  }
}

export function saveCart(items: CartItem[]): void {
  localStorage.setItem(KEY, JSON.stringify(items));
  window.dispatchEvent(new CustomEvent('cart:updated'));
}

export function addToCart(item: Omit<CartItem, 'cantidad'>, qty = 1): void {
  const cart = getCart();
  const found = cart.find((i) => i.id === item.id);
  if (found) {
    found.cantidad += qty;
  } else {
    cart.push({ ...item, cantidad: qty });
  }
  saveCart(cart);
}

export function cartTotal(items: CartItem[] = getCart()): number {
  return items.reduce((sum, i) => sum + i.precio * i.cantidad, 0);
}

export function clearCart(): void {
  localStorage.removeItem(KEY);
  window.dispatchEvent(new CustomEvent('cart:updated'));
}
