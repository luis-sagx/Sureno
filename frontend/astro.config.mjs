// @ts-check
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';
import tailwindcss from '@tailwindcss/vite';

// URL del backend Flask (API JSON). Configurable por entorno.
const FLASK_API = process.env.FLASK_API_URL || 'http://localhost:5000';

// https://astro.build/config
export default defineConfig({
  output: 'server',
  adapter: node({ mode: 'standalone' }),
  server: { port: 4321 },
  vite: {
    plugins: [tailwindcss()],
    server: {
      // Dev: el navegador habla solo con Astro; /api se reenvia a Flask
      // (same-origin -> la cookie de sesion y CSRF funcionan sin CORS).
      proxy: {
        '/api': { target: FLASK_API, changeOrigin: true },
        // Imágenes/estáticos servidos por Flask (uploads de productos).
        '/static': { target: FLASK_API, changeOrigin: true },
      },
    },
  },
});
