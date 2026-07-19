import { test, expect } from '@playwright/test';
import { snap, TEST_USER } from './helpers';

// TAR-04 / issue #21: flujo E2E de login.
// login.astro no usa alert() nativo (verificado leyendo el código: usa un
// <p data-error> inline), pero por si algún flujo dispara un dialog nativo
// (p.ej. confirm() en /compras al cancelar un pedido) registramos un
// handler de 'dialog' en todos los tests para no bloquear el navegador.
test.beforeEach(({ page }) => {
  page.on('dialog', (dialog) => dialog.accept());
});

test.describe('Login', () => {
  test('login exitoso con credenciales válidas redirige fuera de /login', async ({ page }) => {
    await page.goto('/login');
    await snap(page, 'login-form-vacio');

    await page.fill('input[name="email"]', TEST_USER.email);
    await page.fill('input[name="password"]', TEST_USER.password);
    await snap(page, 'login-form-completo');

    await page.click('button[type="submit"]');
    await page.waitForURL((url) => !url.pathname.startsWith('/login'), { timeout: 10_000 });

    // Header debe reflejar sesión iniciada: el menú de perfil (details/summary)
    // contiene el link "Mis compras", visible al abrir el desplegable.
    await page.locator('header details summary').click();
    await expect(page.locator('header a[href="/compras"]')).toBeVisible();
    await snap(page, 'login-exitoso-home');
  });

  test('login fallido muestra error inline sin redirigir', async ({ page }) => {
    await page.goto('/login');

    await page.fill('input[name="email"]', TEST_USER.email);
    await page.fill('input[name="password"]', 'contraseña-incorrecta-xyz');
    await page.click('button[type="submit"]');

    const errorBox = page.locator('[data-error]');
    await expect(errorBox).toBeVisible({ timeout: 10_000 });
    await expect(errorBox).not.toBeEmpty();
    await expect(page).toHaveURL(/\/login$/);
    await snap(page, 'login-fallido-error-inline');
  });
});
