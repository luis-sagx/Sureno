import { defineConfig, devices } from '@playwright/test';

/**
 * Configuración de Playwright para la suite E2E de Sureño (TAR-04 / issue #21).
 *
 * Requiere el stack completo corriendo ANTES de ejecutar los tests:
 *
 *   # Terminal 1 - backend Flask (venv Python 3.11 + backend/.env con MONGO_URI)
 *   cd backend && source ../venv/bin/activate && python app.py
 *
 *   # Terminal 2 - frontend Astro (SSR, proxea /api y /static al backend)
 *   cd frontend && npm run dev
 *
 * No se automatiza el arranque de ambos servidores (`webServer`) porque el
 * backend necesita un virtualenv Python 3.11 + credenciales reales de
 * MongoDB Atlas (backend/.env) que Playwright no puede provisionar; forzar
 * un arranque automático aquí sería frágil. Ver README en tests-e2e/.
 *
 * Ejecutar:
 *   npx playwright test
 */
export default defineConfig({
  testDir: './tests-e2e',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [['list'], ['html', { outputFolder: 'tests-e2e/playwright-report', open: 'never' }]],
  timeout: 30_000,
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:4321',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'off',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
