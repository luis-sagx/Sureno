# Informe de carga — TAR-05 (#22) Pruebas de carga/rendimiento (Locust)

## Configuración de la corrida

- Herramienta: Locust 2.45.0
- SUT: `backend/app.py` (Flask dev server, `python app.py`, `use_reloader=False`), Python 3.11.15
- Base de datos: MongoDB Atlas de **prueba** (RY-01), conexión vía `backend/.env` existente localmente (no versionado)
- Host objetivo: `http://localhost:5000`
- Perfiles: `VisitanteAnonimo` (catálogo público: `GET /api/products`, `GET /api/products/:id`, `GET /api/categories`, `GET /api/csrf`) y `ClienteQueIniciaSesion` (`GET /api/csrf` + `POST /api/login` con credenciales de prueba `ingresoSureno@gmail.com`)
- Carga: 50 usuarios concurrentes, spawn-rate 5 usuarios/s, duración 2 minutos, modo headless
- Comando ejecutado (documentado también en el docstring de `Tests/carga/locustfile.py` y en `Tests/README.md`):

```bash
locust -f Tests/carga/locustfile.py --host http://localhost:5000 \
  --users 50 --spawn-rate 5 --run-time 2m --headless \
  --html Tests/evidencias/reporte_carga.html \
  --csv  Tests/evidencias/carga
```

## Nota sobre el locustfile

El `locustfile.py` original apuntaba a rutas HTML que ya no existen en el
backend (`/`, `/index`, `/login`, `/signUp`, `/about`, `/contact`) — el
proyecto migró a una API JSON pura bajo `/api`, servida a un frontend Astro
separado (ver `app.py`, `routes/__init__.py`). Se actualizó el locustfile
para golpear los endpoints reales y públicos (`/api/products`,
`/api/products/:id`, `/api/categories`, `/api/csrf`) y el login real
(`POST /api/login`), incluyendo el manejo de CSRF (`CSRFProtect` global en
`app.py`): el perfil de login hace primero `GET /api/csrf` para sembrar la
cookie de sesión + token, y reenvía el token en la cabecera `X-CSRFToken`,
igual que hace el frontend Astro en producción.

## Resultados (evidencia completa en `carga_stats.csv` / `reporte_carga.html`)

Total de la corrida: **2694 requests, 0 fallos (0.00%)**.

| Endpoint | # reqs | Fallos | RPS | p50 | p95 | p99 | Max |
|---|---:|---:|---:|---:|---:|---:|---:|
| GET /api/products | 610 | 0 | 5.12 | 110 ms | 140 ms | 310 ms | 920 ms |
| GET /api/products/:id | 366 | 0 | 3.07 | 210 ms | 270 ms | 510 ms | 756 ms |
| GET /api/categories | 249 | 0 | 2.09 | 110 ms | 140 ms | 230 ms | 275 ms |
| GET /api/csrf (anónimo) | 129 | 0 | 1.08 | 6 ms | 8 ms | 16 ms | 17 ms |
| GET /api/csrf (previo a login) | 673 | 0 | 5.65 | 6 ms | 11 ms | 17 ms | 32 ms |
| POST /api/login | 667 | 0 | 5.60 | 860 ms | 960 ms | 1300 ms | 1543 ms |
| **Agregado** | **2694** | **0** | **22.62** | **110 ms** | **890 ms** | **1000 ms** | **1543 ms** |

- **RPS agregado:** ~22.6 req/s sostenido con 50 usuarios concurrentes.
- **% de fallos:** 0.00% (0 de 2694 requests) — ningún timeout, error 4xx/5xx
  inesperado ni excepción del cliente (`carga_failures.csv` y
  `carga_exceptions.csv` vacíos salvo cabecera).
- **Latencia p50/p95/p99 agregada:** 110 ms / 890 ms / 1000 ms (máximo absoluto 1543 ms).

## Interpretación

- Los endpoints de solo lectura sin operaciones costosas (`/api/csrf`,
  `/api/categories`) responden en pocos milisegundos incluso bajo carga.
- `POST /api/login` es, con diferencia, el endpoint más lento (p50 ≈ 860 ms,
  p99 ≈ 1.3 s) porque cada intento ejecuta `bcrypt.checkpw` (hash costoso
  por diseño) más una consulta a Mongo Atlas por la red; a 50 usuarios
  concurrentes esto empieza a notarse pero **no genera ningún fallo ni
  timeout**, es decir el sistema absorbe la carga, solo con más latencia.
- **Caveat importante:** el SUT se ejecutó con el servidor de desarrollo de
  Flask (`app.run(...)`, sin `use_reloader`), que es **single-threaded /
  single-process** por defecto. Esto satura antes de lo que lo haría un
  despliegue real con `gunicorn` (ya incluido en `requirements.txt`) y
  varios workers; los tiempos aquí reportados son por tanto un límite
  inferior conservador de lo que daría un backend en producción con
  concurrencia real a nivel de proceso/hilo. Aun así, 0% de fallos con 50
  usuarios concurrentes es un resultado saludable para el alcance de esta
  prueba de carga.

## Cierre del criterio de aceptación (TAR-05 / #22)

- [x] `Tests/carga/locustfile.py` con perfiles anónimo y con login (actualizado a los endpoints reales de la API).
- [x] Reporte HTML generado: `backend/Tests/evidencias/reporte_carga.html`.
- [x] Reporte CSV generado: `backend/Tests/evidencias/carga_stats.csv`,
      `carga_stats_history.csv`, `carga_failures.csv`, `carga_exceptions.csv`.
- [x] Métricas medidas y documentadas en este informe: RPS, p50/p95/p99, % de fallos.
