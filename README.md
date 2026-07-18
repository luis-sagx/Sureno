# Sureño

E-commerce de licores de la marca Sureño. Arquitectura desacoplada: un backend
Flask que expone una **API JSON pura** sobre MongoDB, y un frontend **Astro (SSR)
con Tailwind** que consume esa API.

## Estructura del proyecto

```
.
├── backend/            # API Flask (JSON) + MongoDB
│   ├── app.py          # App Flask, endpoints /api/*
│   ├── config.py       # Conexión a MongoDB (lee MONGO_URI del entorno)
│   ├── models/         # Modelos de datos (User, Product, Order, Address, Category)
│   ├── routes/         # Blueprints de la API + decoradores de auth
│   ├── static/         # Imágenes de productos (uploads) servidas por Flask
│   ├── Tests/          # Suite pytest (unitarias, integración, carga)
│   ├── scripts/        # Utilidades (coverage para Sonar)
│   ├── requirements.txt / requirements-dev.txt
│   └── .env(.example)  # MONGO_URI, SECRET_KEY, FLASK_DEBUG (no se versiona)
├── frontend/           # App Astro (SSR) + Tailwind
│   └── src/            # pages/, components/, layouts/, lib/, middleware.ts
├── docs/               # Documentación del SQAP
├── .github/workflows/  # CI (SonarCloud)
└── sonar-project.properties
```

El frontend habla solo con su propio origen: el middleware de Astro
(`frontend/src/middleware.ts`) proxya `/api` y `/static` al backend Flask, con lo
que la cookie de sesión y la protección CSRF funcionan sin CORS.

## Características

- Registro y autenticación por sesión, con roles cliente/administrador.
- Catálogo de productos, carrito (localStorage) y proceso de compra.
- Historial de pedidos con cancelación.
- Panel de administración: métricas, gestión de pedidos y CRUD de productos.
- Seguridad: CSRF (Flask-WTF), secretos por variables de entorno, guards de sesión/rol.

## Tecnologías

- **Backend**: Python, Flask (API JSON), Flask-WTF, MongoDB Atlas (PyMongo).
- **Frontend**: Astro (SSR, adaptador Node), Tailwind CSS v4, TypeScript.
- **Pruebas**: pytest + mongomock (backend).

## Puesta en marcha (desarrollo)

### 1. Backend (Flask, puerto 5000)

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # define MONGO_URI, SECRET_KEY; usa FLASK_DEBUG=1 en local
python app.py
```

> En local usa `FLASK_DEBUG=1` para que la cookie CSRF no exija HTTPS.

### 2. Frontend (Astro, puerto 4321)

```bash
cd frontend
npm install
npm run dev                 # o: npm run build && npm start
```

Abre http://localhost:4321. Las llamadas a `/api` se proxyan al backend en `:5000`
(configurable con `FLASK_API_URL`).

## Pruebas (backend)

```bash
cd backend
source venv/bin/activate
pip install -r requirements-dev.txt
pytest                      # unitarias + integración (mongomock, sin Atlas)
```

## SonarCloud

El workflow `.github/workflows/sonar.yml` genera el reporte de cobertura y ejecuta
el análisis. Config en `sonar-project.properties` (fuentes bajo `backend/`,
`sonar.python.coverage.reportPaths=backend/coverage.xml`).
