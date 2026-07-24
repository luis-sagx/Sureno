// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { bindAddToCartButtons } from '@/lib/product-actions';
import { getCart } from '@/lib/cart';

function render(): void {
  document.body.innerHTML = `
    <div data-toast style="opacity: 0"></div>
    <button data-add data-id="p1" data-nombre="Ron Sureño" data-precio="12.5"
            data-imagen="/rum.png" data-mililitros="750">Agregar</button>
    <button data-add data-id="p2" data-nombre="Whisky Sureño" data-precio="30"
            data-imagen="/whisky.png">Agregar</button>`;
}

const clickAdd = (id: string) => document.querySelector<HTMLButtonElement>(`[data-id="${id}"]`)!.click();
const toast = () => document.querySelector<HTMLElement>('[data-toast]')!;

describe('bindAddToCartButtons', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.useFakeTimers();
    render();
  });

  it('adds the product read from the dataset to the cart', () => {
    bindAddToCartButtons();

    clickAdd('p1');

    expect(getCart()).toEqual([
      { id: 'p1', nombre: 'Ron Sureño', precio: 12.5, imagen: '/rum.png', mililitros: 750, cantidad: 1 },
    ]);
  });

  it('leaves mililitros undefined when the button does not declare it', () => {
    bindAddToCartButtons();

    clickAdd('p2');

    expect(getCart()[0].mililitros).toBeUndefined();
  });

  it('shows the toast and hides it after the timeout', () => {
    bindAddToCartButtons();

    clickAdd('p1');

    expect(toast().textContent).toBe('"Ron Sureño" agregado al carrito');
    expect(toast().style.opacity).toBe('1');

    vi.advanceTimersByTime(1600);
    expect(toast().style.opacity).toBe('0');
  });

  it('still adds to the cart when there is no toast element', () => {
    toast().remove();
    bindAddToCartButtons();

    clickAdd('p1');

    expect(getCart()).toHaveLength(1);
  });

  it('accumulates the quantity when the same product is added twice', () => {
    bindAddToCartButtons();

    clickAdd('p1');
    clickAdd('p1');

    expect(getCart()[0].cantidad).toBe(2);
  });
});
