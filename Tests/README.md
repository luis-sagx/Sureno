# Carpeta de Pruebas — SUT Sureno

Suite de aseguramiento de calidad del proyecto. Requiere el entorno de la
[Fase 0](../FASE_0.md) preparado (venv Python 3.11 + `requirements-dev.txt`).

## Estructura

| Carpeta | Tipo de prueba | Herramienta |
|---|---|---|
| `unitarias/` | Unitaria (lógica de `models/` aislada) | pytest + mongomock |
| `integracion/` | Integración (rutas HTTP + sesión + BD) | Flask test client |
| `funcionales/` | Funcional / E2E (flujos de usuario reales) | Selenium |
| `carga/` | Carga / Rendimiento (concurrencia) | Locust |
| `evidencias/` | Screenshots y reportes HTML (entregables) | — |
| `conftest.py` | Fixtures compartidas (se crea en Fase 6) | pytest |

## Requisitos previos

```bash
source venv/bin/activate
pip install -r requirements-dev.txt   # o los paquetes de la Fase 0.2
```

## Ejecutar

### Unitarias + Integración (con cobertura y reporte HTML)

```bash
pytest Tests/unitarias Tests/integracion \
  --cov=models --cov=routes --cov=app \
  --cov-report=xml:coverage.xml \
  --cov-report=html:Tests/evidencias/coverage_html \
  --html=Tests/evidencias/reporte_pytest.html --self-contained-html -v
```

- `coverage.xml` → lo importa SonarCloud.
- `Tests/evidencias/reporte_pytest.html` → evidencia para el PDF.

### Funcionales (Selenium)

Requiere el SUT corriendo en otra terminal (`python app.py`) y Chrome instalado.

```bash
pytest Tests/funcionales --html=Tests/evidencias/reporte_selenium.html --self-contained-html -v
```

### Carga (Locust)

Requiere el SUT corriendo contra una **BD de prueba** (nunca Atlas de producción).

```bash
# Modo interactivo (UI en http://localhost:8089)
locust -f Tests/carga/locustfile.py --host http://localhost:5000

# Headless con reporte para el PDF (50 usuarios, 2 min)
locust -f Tests/carga/locustfile.py --host http://localhost:5000 \
  --users 50 --spawn-rate 5 --run-time 2m --headless \
  --html Tests/evidencias/reporte_carga.html \
  --csv  Tests/evidencias/carga
```

## Convención de nombres

Los tests referencian su caso de prueba y requisito en el nombre y docstring:

```python
def test_cp04_login_exitoso_cliente(client, usuario_cliente):
    """CP-04 / RF-02: login válido responde 200 con redirect a /index."""
```

Esto mantiene la **trazabilidad** requisito ↔ caso ↔ código exigida por la matriz
de la Fase 5.
