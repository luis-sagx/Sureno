import { test, expect } from '@playwright/test';

const protectedRoutes = [
  { path: '/cart', name: 'carrito' },
  { path: '/checkout?cart_id=sin-sesion', name: 'checkout' },
  { path: '/compras', name: 'historial de compras' },
  { path: '/admin', name: 'panel administrativo' },
  { path: '/admin/products', name: 'productos administrativos' },
];

test.describe('Control de acceso', () => {
  for (const route of protectedRoutes) {
    test(`redirige ${route.name} al login sin sesión`, async ({ page }) => {
      await page.goto(route.path);

      await expect(page).toHaveURL(/\/login$/);
      await expect(page.getByRole('heading', { name: 'Iniciar sesión' })).toBeVisible();
    });
  }
});
