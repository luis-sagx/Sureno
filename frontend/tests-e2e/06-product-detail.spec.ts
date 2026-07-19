import { test, expect } from '@playwright/test';

test('abre el detalle del producto seleccionado desde el catálogo', async ({ page }) => {
  await page.goto('/products');

  const firstCard = page.locator('.panel.card-hover').first();
  await expect(firstCard).toBeVisible();
  const productName = (await firstCard.locator('h5').innerText()).trim();

  await firstCard.getByRole('link', { name: /Ver más información/ }).click();

  await expect(page).toHaveURL(/\/products\/[^/]+$/);
  await expect(page.getByRole('heading', { name: productName, exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: /Agregar al carrito/ })).toBeVisible();
});
