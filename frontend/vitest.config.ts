/// <reference types="vitest/config" />
import { getViteConfig } from 'astro/config';

export default getViteConfig({
  test: {
    environment: 'node',
    include: ['tests/**/*.test.ts'],
    restoreMocks: true,
    coverage: {
      provider: 'v8',
      // html -> evidencia navegable; json-summary alimenta el calculador de
      // metricas (metricas/calcular_metricas.py, MC-11); lcov lo importa Sonar.
      reporter: ['text', 'html', 'lcov', 'json-summary'],
      reportsDirectory: 'coverage',
      include: ['src/lib/**/*.ts', 'src/middleware.ts'],
    },
  },
});
