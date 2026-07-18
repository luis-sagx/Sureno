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
"""
from locust import HttpUser, task, between

# Credenciales de prueba (mismas del README del SUT).
CLIENTE = {"email": "ingresoSureno@gmail.com", "password": "ingreso1"}


class VisitanteAnonimo(HttpUser):
    """Simula navegacion publica: la mayoria del trafico real de un e-commerce
    es lectura de catalogo sin autenticarse."""

    wait_time = between(1, 3)  # think-time entre peticiones (s)

    @task(5)
    def ver_index(self):
        self.client.get("/index", name="GET /index")

    @task(3)
    def ver_home(self):
        self.client.get("/", name="GET /")

    @task(2)
    def ver_login(self):
        self.client.get("/login", name="GET /login (form)")

    @task(1)
    def ver_signup(self):
        self.client.get("/signUp", name="GET /signUp (form)")

    @task(1)
    def ver_about(self):
        self.client.get("/about", name="GET /about")

    @task(1)
    def ver_contact(self):
        self.client.get("/contact", name="GET /contact")


class ClienteQueIniciaSesion(HttpUser):
    """Simula el flujo de autenticacion: POST /login recibe JSON
    (verificado en Fase 6) y responde JSON con 'redirect'."""

    wait_time = between(2, 5)

    @task
    def login(self):
        with self.client.post(
            "/login", json=CLIENTE, name="POST /login", catch_response=True
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"login fallo: HTTP {resp.status_code}")
