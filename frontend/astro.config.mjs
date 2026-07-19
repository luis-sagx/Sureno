// @ts-check
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';
import icon from 'astro-icon';
import tailwindcss from '@tailwindcss/vite';
import { loadEnv } from 'vite';

// URL del backend Flask (API JSON). Configurable por entorno.
const env = loadEnv(process.env.NODE_ENV || 'development', process.cwd(), '');
const FLASK_API = process.env.FLASK_API_URL || env.FLASK_API_URL || 'http://127.0.0.1:5000';

// https://astro.build/config
export default defineConfig({
  output: 'server',
  adapter: node({ mode: 'standalone' }),
  integrations: [icon()],
  server: { port: 4321 },
  // El proxy reenvía formularios multipart a Flask, que ya valida CSRF
  // (Flask-WTF). La verificación de origen de Astro bloquearía esos POST.
  security: { checkOrigin: false },
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
