import { test, expect } from '@playwright/test';

test.describe('Navegación pública', () => {
  test('la llamada principal abre el catálogo', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByText('Calidad en tu paladar')).toBeVisible();
    await page.getByRole('link', { name: /Comprar Ahora/ }).click();

    await expect(page).toHaveURL(/\/products$/);
    await expect(page.getByRole('heading', { name: 'Productos Sureño' })).toBeVisible();
  });

  test('la página institucional muestra historia, misión y visión', async ({ page }) => {
    await page.goto('/about');

    await expect(page.getByRole('heading', { name: 'Nuestra Historia' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Misión' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Visión' })).toBeVisible();
  });

  test('la página de contacto publica los canales de atención', async ({ page }) => {
    await page.goto('/contact');

    await expect(page.getByRole('heading', { name: '¡Hablemos!' })).toBeVisible();
    await expect(page.getByText('licorsureno@gmail.com')).toBeVisible();
    await expect(page.getByRole('link', { name: 'WhatsApp' })).toHaveAttribute('href', 'tel:+593967967369');
  });

  test('el tema oscuro se conserva después de recargar', async ({ page }) => {
    await page.goto('/');

    const themeToggle = page.getByRole('switch', { name: 'Cambiar tema' });
    await themeToggle.click();
    await expect(page.locator('html')).toHaveClass(/dark/);
    await expect.poll(() => page.evaluate(() => localStorage.getItem('theme'))).toBe('dark');

    await page.reload();
    await expect(page.locator('html')).toHaveClass(/dark/);
  });

  test('el menú móvil abre y permite navegar', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/');

    const menuButton = page.locator('[data-menu-toggle]');
    await expect(menuButton).toHaveAccessibleName('Abrir menú');
    await menuButton.click();
    await expect(menuButton).toHaveAttribute('aria-expanded', 'true');
    await expect(menuButton).toHaveAccessibleName('Cerrar menú');

    await page.locator('[data-main-nav]').getByRole('link', { name: 'Quiénes Somos' }).click();
    await expect(page).toHaveURL(/\/about$/);
  });
});
