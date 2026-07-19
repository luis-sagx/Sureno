import { test, expect, type Page } from '@playwright/test';

async function fillSignup(page: Page, email: string, identification: string) {
  await page.fill('input[name="nombre"]', 'Usuario');
  await page.fill('input[name="apellido"]', 'Prueba');
  await page.fill('input[name="cedula"]', identification);
  await page.fill('input[name="email"]', email);
  await page.fill('input[name="password"]', 'Clave123');
  await page.click('button[type="submit"]');
}

test.describe('Registro', () => {
  test('permite navegar entre login y registro', async ({ page }) => {
    await page.goto('/login');
    await page.getByRole('link', { name: 'Regístrate' }).click();
    await expect(page).toHaveURL(/\/signup$/);
    await expect(page.getByRole('heading', { name: 'Crear cuenta' })).toBeVisible();

    await page.getByRole('link', { name: 'Inicia sesión' }).click();
    await expect(page).toHaveURL(/\/login$/);
  });

  test('rechaza un correo con formato inválido', async ({ page }) => {
    await page.goto('/signup');
    await fillSignup(page, 'correo-invalido', '1710034065');

    await expect(page.locator('[data-error]')).toContainText('Email inválido');
    await expect(page).toHaveURL(/\/signup$/);
  });

  test('rechaza una cédula o RUC inválido', async ({ page }) => {
    await page.goto('/signup');
    await fillSignup(page, 'registro-e2e@test.com', '123');

    await expect(page.locator('[data-error]')).toContainText('Cédula o RUC inválido');
    await expect(page).toHaveURL(/\/signup$/);
  });
});
