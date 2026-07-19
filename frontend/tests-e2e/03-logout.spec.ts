import { test, expect } from '@playwright/test';
import { snap, TEST_USER } from './helpers';

// TAR-04 / issue #21: tercer flujo E2E — cierre de sesión y protección de
// rutas. Login -> verificar sesión activa -> logout -> confirmar que una
// ruta protegida (/compras, guardada por el middleware de Astro) redirige
// de nuevo a /login.
test.beforeEach(({ page }) => {
  page.on('dialog', (dialog) => dialog.accept());
});

test('logout cierra la sesión y bloquea rutas protegidas', async ({ page }) => {
  await page.goto('/login');
  await page.fill('input[name="email"]', TEST_USER.email);
  await page.fill('input[name="password"]', TEST_USER.password);
  await page.click('button[type="submit"]');
  await page.waitForURL((url) => !url.pathname.startsWith('/login'), { timeout: 10_000 });

  // El link de logout vive dentro del menú de perfil (details/summary),
  // hay que abrirlo antes de poder verlo/clickearlo.
  await page.locator('header details summary').click();
  const logoutLink = page.locator('[data-logout]');
  await expect(logoutLink).toBeVisible();
  await snap(page, 'logout-sesion-activa');

  await logoutLink.click();
  await page.waitForURL(/\/login$/, { timeout: 10_000 });
  await snap(page, 'logout-redirigido-a-login');

  // Sin sesión, /compras (ruta protegida por middleware) debe rebotar a /login.
  await page.goto('/compras');
  await page.waitForURL(/\/login$/, { timeout: 10_000 });
  await snap(page, 'logout-ruta-protegida-bloqueada');
});
