import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('@/lib/api', () => ({ apiServer: vi.fn() }));

import { apiServer } from '@/lib/api';
import HomePage from '@/pages/index.astro';
import LoginPage from '@/pages/login.astro';
import ProductsPage from '@/pages/products/index.astro';
import AdminHomePage from '@/pages/admin/home.astro';

async function render(component: Parameters<AstroContainer['renderToString']>[0], path: string) {
  const container = await AstroContainer.create();
  return container.renderToString(component, {
    request: new Request(`http://astro.local${path}`),
    partial: false,
  });
}

describe('Astro SSR pages', () => {
  beforeEach(() => vi.mocked(apiServer).mockReset());

  it('renders the home page and its primary catalog action', async () => {
    const html = await render(HomePage, '/');
    expect(html).toContain('<title>Sureño — Inicio</title>');
    expect(html).toContain('Calidad en tu paladar');
    expect(html).toContain('href="/products"');
  });

  it('renders the login form with accessible fields', async () => {
    const html = await render(LoginPage, '/login');
    expect(html).toContain('<title>Sureño — Iniciar sesión</title>');
    expect(html).toContain('id="login-form"');
    expect(html).toContain('type="email"');
    expect(html).toContain('type="password"');
  });

  it('renders products returned by the mocked backend', async () => {
    vi.mocked(apiServer).mockResolvedValue({
      ok: true,
      status: 200,
      data: [{ _id: 'p1', nombre: 'Aguardiente Diamante', precio: 19.9, imagen: '/p1.png' }],
    });

    const html = await render(ProductsPage, '/products');
    expect(html).toContain('Aguardiente Diamante');
    expect(html).toContain('Precio: $19.90');
    expect(html).toContain('data-id="p1"');
  });

  it('renders the catalog error state without a live backend', async () => {
    vi.mocked(apiServer).mockResolvedValue({
      ok: false, status: 0, data: null, error: 'offline',
    });

    const html = await render(ProductsPage, '/products');
    expect(html).toContain('No se pudo cargar el catálogo');
    expect(html).not.toContain('data-add');
  });

  it('renders admin totals and order states from mocked responses', async () => {
    vi.mocked(apiServer)
      .mockResolvedValueOnce({
        ok: true, status: 200,
        data: { total_clientes: 8, total_productos: 12, total_pedidos: 3 },
      })
      .mockResolvedValueOnce({
        ok: true, status: 200,
        data: [{ estado: 'pendiente' }, { estado: 'entregado' }, { estado: 'entregado' }],
      });

    const html = await render(AdminHomePage, '/admin/home');
    expect(html).toContain('Dashboard');
    expect(html).toContain('Total de pedidos registrados: 3');
    expect(html).toContain('Pendientes');
    expect(html).toContain('Entregados');
  });
});
