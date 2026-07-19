// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { addToCart, cartTotal, clearCart, getCart, saveCart } from '@/lib/cart';

const product = {
  id: 'rum-1',
  nombre: 'Ron Sureño',
  precio: 12.5,
  imagen: '/rum.png',
};

describe('cart', () => {
  beforeEach(() => localStorage.clear());

  it('returns an empty cart when storage is missing or malformed', () => {
    expect(getCart()).toEqual([]);
    localStorage.setItem('cart', '{invalid');
    expect(getCart()).toEqual([]);
    localStorage.setItem('cart', '{"id":"not-an-array"}');
    expect(getCart()).toEqual([]);
  });

  it('saves a cart and notifies the UI', () => {
    const listener = vi.fn();
    window.addEventListener('cart:updated', listener, { once: true });
    saveCart([{ ...product, cantidad: 2 }]);

    expect(getCart()).toEqual([{ ...product, cantidad: 2 }]);
    expect(listener).toHaveBeenCalledOnce();
  });

  it('adds a new product with the requested quantity', () => {
    addToCart(product, 3);
    expect(getCart()).toEqual([{ ...product, cantidad: 3 }]);
  });

  it('increments the quantity of an existing product', () => {
    saveCart([{ ...product, cantidad: 1 }]);
    addToCart(product, 2);
    expect(getCart()[0].cantidad).toBe(3);
  });

  it('calculates totals and clears persisted items', () => {
    expect(cartTotal([{ ...product, cantidad: 2 }])).toBe(25);
    saveCart([{ ...product, cantidad: 2 }]);
    clearCart();
    expect(getCart()).toEqual([]);
  });
});
