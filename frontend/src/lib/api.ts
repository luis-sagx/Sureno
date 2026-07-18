// Cliente de la API Flask para uso SERVER-SIDE en Astro (.astro frontmatter,
// endpoints, middleware). Reenvia la cookie del navegador para conservar la
// sesion de Flask. En cliente usa fetch('/api/...') directo (lo proxya vite).

const FLASK_API = import.meta.env.FLASK_API_URL || 'http://localhost:5000';

export interface ApiResult<T> {
  ok: boolean;
  status: number;
  data: T | null;
  error?: string;
}

/**
 * Llama a la API Flask desde el servidor Astro, reenviando la cookie de sesion
 * del request entrante para que la autenticacion funcione.
 */
export async function apiServer<T = unknown>(
  path: string,
  request: Request,
  init: RequestInit = {},
): Promise<ApiResult<T>> {
  const cookie = request.headers.get('cookie') ?? '';
  const url = `${FLASK_API}${path.startsWith('/') ? path : `/${path}`}`;

  try {
    const res = await fetch(url, {
      ...init,
      headers: {
        Accept: 'application/json',
        ...(init.body ? { 'Content-Type': 'application/json' } : {}),
        cookie,
        ...(init.headers ?? {}),
      },
    });

    const text = await res.text();
    let data: T | null = null;
    try {
      data = text ? (JSON.parse(text) as T) : null;
    } catch {
      data = null; // respuesta no-JSON
    }

    return {
      ok: res.ok,
      status: res.status,
      data,
      error: res.ok ? undefined : (data as any)?.error ?? res.statusText,
    };
  } catch (err) {
    return { ok: false, status: 0, data: null, error: String(err) };
  }
}

/** Devuelve el usuario autenticado o null (para middleware / guards). */
export async function getSessionUser(request: Request) {
  const r = await apiServer<{ email: string; nombre: string }>('/api/user', request);
  return r.ok ? r.data : null;
}
