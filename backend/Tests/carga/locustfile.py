"""Pruebas de carga / rendimiento del SUT Sureno (Fase 2.1 - Locust).

Requiere el SUT corriendo en otra terminal:
    python app.py            # con MONGO_URI apuntando a una BD de PRUEBA

Ejecutar (UI web en http://localhost:8089):
    locust -f Tests/carga/locustfile.py --host http://localhost:5000

Ejecutar headless y exportar reporte (evidencia para el PDF, Fase 9):
    locust -f Tests/carga/locustfile.py --host http://localhost:5000 \
        --users 50 --spawn-rate 5 --run-time 2m --headless \
        --html Tests/evidencias/reporte_carga.html \
        --csv  Tests/evidencias/carga

Métricas a reportar: RPS, latencia p50/p95/p99, % de fallos.
NOTA: usar SIEMPRE una BD de prueba separada (RY-01). No lanzar carga
contra MongoDB Atlas de produccion.

NOTA (actualizacion post refactor a API JSON pura, ver Fase 6 / DEF-015):
el backend ya no sirve HTML (/, /index, /login, /signUp, ... viven ahora en
el frontend Astro, fuera del alcance de este SUT). Los perfiles de carga
se apuntan por eso a los endpoints JSON reales bajo /api que SI sirve este
backend: /api/products, /api/categories, /api/csrf y /api/login (esta
ultima protegida con CSRF global, ver app.py:22 CSRFProtect(app), por lo
que el perfil autenticado primero hace GET /api/csrf para sembrar la
cookie+token antes del POST).
"""
from locust import HttpUser, task, between

# Credenciales de prueba (mismas del README del SUT).
CLIENTE = {"email": "ingresoSureno@gmail.com", "password": "ingreso1"}

# Producto real de la BD de pruebas (catalogo semilla), usado para el
# endpoint de detalle GET /api/products/<id>.
PRODUCTO_ID_MUESTRA = "67aa7c941e02dfc22ada42bf"


class VisitanteAnonimo(HttpUser):
    """Simula navegacion publica: la mayoria del trafico real de un e-commerce
    es lectura de catalogo sin autenticarse. Todos estos endpoints son
    publicos (sin @login_required_api / @admin_required_api)."""

    wait_time = between(1, 3)  # think-time entre peticiones (s)

    @task(5)
    def ver_productos(self):
        self.client.get("/api/products", name="GET /api/products")

    @task(3)
    def ver_producto_detalle(self):
        self.client.get(
            f"/api/products/{PRODUCTO_ID_MUESTRA}",
            name="GET /api/products/:id",
        )

    @task(2)
    def ver_categorias(self):
        self.client.get("/api/categories", name="GET /api/categories")

    @task(1)
    def obtener_csrf(self):
        self.client.get("/api/csrf", name="GET /api/csrf")


class ClienteQueIniciaSesion(HttpUser):
    """Simula el flujo de autenticacion: GET /api/csrf para sembrar la
    cookie de sesion + token, y luego POST /api/login (protegido con CSRF)
    que responde JSON con 'redirect' si las credenciales son validas."""

    wait_time = between(2, 5)

    @task
    def login(self):
        csrf_resp = self.client.get("/api/csrf", name="GET /api/csrf (login)")
        try:
            token = csrf_resp.json().get("csrfToken")
        except ValueError:
            token = None

        headers = {"X-CSRFToken": token} if token else {}
        with self.client.post(
            "/api/login", json=CLIENTE, headers=headers,
            name="POST /api/login", catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"login fallo: HTTP {resp.status_code}")
