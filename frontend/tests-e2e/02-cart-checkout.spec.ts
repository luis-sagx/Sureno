import { test, expect } from '@playwright/test';
import { snap, TEST_USER } from './helpers';

// TAR-04 / issue #21: flujo E2E carrito -> checkout.
// Cubre: login, agregar producto del catálogo al carrito (localStorage),
// verificar carrito (ítem + total), y completar el checkout (dirección +
// finalizar compra) hasta la confirmación (redirect a /compras con el
// pedido nuevo listado).
test.beforeEach(({ page }) => {
  page.on('dialog', (dialog) => dialog.accept());
});

async function login(page: import('@playwright/test').Page) {
  await page.goto('/login');
  await page.fill('input[name="email"]', TEST_USER.email);
  await page.fill('input[name="password"]', TEST_USER.password);
  await page.click('button[type="submit"]');
  await page.waitForURL((url) => !url.pathname.startsWith('/login'), { timeout: 10_000 });
}

test('agregar producto al carrito y completar checkout', async ({ page }) => {
  await login(page);

  // Limpiar carrito para partir de un estado conocido.
  await page.goto('/products');
  await page.evaluate(() => localStorage.removeItem('cart'));
  await page.reload();

  await expect(page.locator('[data-add]').first()).toBeVisible();
  const firstCard = page.locator('.panel.card-hover').first();
  const nombreProducto = await firstCard.locator('h5').innerText();
  const precioTexto = await firstCard.locator('p.font-bold').innerText(); // "Precio: $X.XX"
  const precio = parseFloat(precioTexto.replace(/[^0-9.]/g, ''));

  await snap(page, 'catalogo-productos');

  await firstCard.locator('[data-add]').click();
  await expect(page.locator('[data-toast]')).toContainText('agregado al carrito');
  await snap(page, 'producto-agregado-toast');

  // Ir al carrito y verificar item + total.
  await page.goto('/cart');
  await expect(page.locator('[data-cart-items]')).toContainText(nombreProducto);
  const totalTexto = await page.locator('[data-total]').innerText();
  const total = parseFloat(totalTexto.replace(/[^0-9.]/g, ''));
  expect(total).toBeCloseTo(precio, 2);
  await snap(page, 'carrito-con-producto');

  // Confirmar productos -> crea carrito en backend y navega a checkout.
  await page.locator('[data-checkout]').click();
  await page.waitForURL(/\/checkout\?cart_id=/, { timeout: 10_000 });
  await expect(page.locator('[data-subtotal]')).toContainText('$');
  await snap(page, 'checkout-resumen-cargado');

  // Completar dirección de entrega.
  await page.selectOption('#canton', 'Rumiñahui');
  await page.fill('#parroquia', 'Sangolquí');
  await page.fill('#calle_principal', 'Av. General Enríquez');
  await page.fill('#calle_secundaria', 'Calle Rocafuerte');
  await page.fill('#codigo_postal', '171103');
  await page.click('#address-form button[type="submit"]');
  await expect(page.locator('[data-address-ok]')).toBeVisible({ timeout: 10_000 });
  await snap(page, 'checkout-direccion-guardada');

  // Finalizar compra -> crea el pedido y redirige a /compras.
  await page.click('#finalizar-compra');
  await page.waitForURL(/\/compras$/, { timeout: 15_000 });
  await snap(page, 'checkout-finalizado-compras');

  // El pedido recién creado debe aparecer como la primera fila de la tabla.
  const firstRow = page.locator('tbody tr').first();
  await expect(firstRow).toContainText(nombreProducto);
  await snap(page, 'historial-compras-nuevo-pedido');
});
