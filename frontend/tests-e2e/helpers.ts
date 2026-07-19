import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
import type { Page } from '@playwright/test';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Evidencia (capturas) se guarda en la carpeta convencional del repo,
// backend/Tests/evidencias/, junto al resto de artefactos de QA
// (reporte_pytest.html, reporte_selenium.html, reporte_carga.html, ...).
export const EVIDENCE_DIR = path.resolve(__dirname, '../../backend/Tests/evidencias');

fs.mkdirSync(EVIDENCE_DIR, { recursive: true });

let counter = 0;

/** Captura de pantalla numerada y con nombre descriptivo para trazabilidad. */
export async function snap(page: Page, name: string): Promise<void> {
  counter += 1;
  const file = path.join(EVIDENCE_DIR, `${String(counter).padStart(2, '0')}-${name}.png`);
  await page.screenshot({ path: file, fullPage: true });
}

// Credenciales de la cuenta de prueba (misma usada en Tests/carga/locustfile.py).
export const TEST_USER = {
  email: 'ingresoSureno@gmail.com',
  password: 'ingreso1',
};
