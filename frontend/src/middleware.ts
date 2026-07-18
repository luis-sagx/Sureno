import { defineMiddleware } from 'astro:middleware';
import { apiServer } from '@/lib/api';

const FLASK_API = import.meta.env.FLASK_API_URL || 'http://localhost:5000';

// Rutas que exigen sesión; y las que además exigen rol administrador.
const USER_PATHS = ['/cart', '/checkout', '/compras'];
const ADMIN_PREFIX = '/admin';

interface SessionUser {
  email: string;
  rol?: string;
}

/**
 * Reenvía /api y /static al backend Flask, conservando cookie, cuerpo y
 * Set-Cookie. Funciona igual en `astro dev` y en el server Node de producción
 * (el proxy de vite solo existe en dev).
 */
async function proxyToFlask(request: Request, url: URL): Promise<Response> {
  const target = `${FLASK_API}${url.pathname}${url.search}`;
  const method = request.method;

  const init: RequestInit = {
    method,
    headers: request.headers,
    redirect: 'manual',
  };
  if (method !== 'GET' && method !== 'HEAD') {
    init.body = await request.arrayBuffer();
  }

  const res = await fetch(target, init);

  // Reconstruir respuesta preservando Set-Cookie (puede ser múltiple).
  const headers = new Headers(res.headers);
  headers.delete('set-cookie');
  const setCookies = (res.headers as any).getSetCookie?.() ?? [];
  for (const c of setCookies) headers.append('set-cookie', c);

  return new Response(res.body, { status: res.status, statusText: res.statusText, headers });
}

export const onRequest = defineMiddleware(async (context, next) => {
  const { url, request } = context;
  const { pathname } = url;

  // 1) Proxy de API y estáticos de Flask.
  if (pathname.startsWith('/api') || pathname.startsWith('/static')) {
    return proxyToFlask(request, url);
  }

  // 2) Guards de sesión / rol.
  const needsUser = USER_PATHS.some((p) => pathname === p || pathname.startsWith(p + '/'));
  const needsAdmin = pathname === ADMIN_PREFIX || pathname.startsWith(ADMIN_PREFIX + '/');

  if (needsUser || needsAdmin) {
    const res = await apiServer<SessionUser>('/api/user', request);
    const user = res.ok ? res.data : null;

    if (!user) return context.redirect('/login');
    if (needsAdmin && user.rol !== 'administrador') return context.redirect('/');
  }

  return next();
});
