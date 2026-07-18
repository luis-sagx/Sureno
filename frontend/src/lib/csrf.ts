// Utilidades CSRF para el CLIENTE. Reenvia el token de la cookie 'csrf_token'
// (que setea Flask) en la cabecera X-CSRFToken de toda peticion mutante.

function getCookie(name: string): string {
  const match = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return match ? decodeURIComponent(match.pop()!) : '';
}

/** Garantiza la cookie csrf_token (Flask la siembra en cualquier respuesta /api). */
async function ensureCsrfToken(): Promise<string> {
  let token = getCookie('csrf_token');
  if (!token) {
    await fetch('/api/csrf', { credentials: 'same-origin' });
    token = getCookie('csrf_token');
  }
  return token;
}

/** fetch con CSRF + credenciales, para llamar la API Flask desde el navegador. */
export async function apiFetch(input: string, init: RequestInit = {}): Promise<Response> {
  const method = (init.method || 'GET').toUpperCase();
  const headers = new Headers(init.headers || {});
  if (!headers.has('Content-Type') && init.body) {
    headers.set('Content-Type', 'application/json');
  }
  if (!/^(GET|HEAD|OPTIONS)$/.test(method)) {
    const token = await ensureCsrfToken();
    if (token) headers.set('X-CSRFToken', token);
  }
  return fetch(input, { ...init, headers, credentials: 'same-origin' });
}
