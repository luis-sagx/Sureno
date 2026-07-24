#!/usr/bin/env bash
# Ejecuta TODA la suite de calidad del SQAP y calcula las metricas ISO.
#
# Este es el comando que se muestra en la exposicion: produce exactamente los
# mismos numeros que aparecen en el documento SQAP_Sureno.tex, porque el
# documento consume las tablas que este script genera
# (metricas/salida/metricas_tabla.tex y trazabilidad_tabla.tex).
#
#   ./metricas/ejecutar_suite.sh            # backend + frontend + estatico + metricas
#   ./metricas/ejecutar_suite.sh --con-e2e  # ademas Playwright (requiere stack levantado)
#   ./metricas/ejecutar_suite.sh --con-carga# ademas Locust    (requiere backend levantado)
#
# Requisitos previos para --con-e2e / --con-carga (dos terminales):
#   cd backend  && source ../venv/bin/activate && python app.py
#   cd frontend && npm run dev
set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${RAIZ}/venv/bin/python"
[[ -x "$PY" ]] || PY="python3"
CON_E2E=0
CON_CARGA=0
for arg in "$@"; do
  case "$arg" in
    --con-e2e)   CON_E2E=1 ;;
    --con-carga) CON_CARGA=1 ;;
    --todo)      CON_E2E=1; CON_CARGA=1 ;;
    *) echo "Opcion desconocida: $arg" >&2; exit 2 ;;
  esac
done

paso() { printf '\n\033[1;36m==> %s\033[0m\n' "$1"; }

# ---------------------------------------------------------------- backend ---
paso "1/5  Backend: pytest (unitarias + integracion) con cobertura y JUnit"
cd "${RAIZ}/backend"
mkdir -p Tests/evidencias
"$PY" -m pytest \
  --junitxml=Tests/evidencias/junit_backend.xml \
  --html=Tests/evidencias/reporte_pytest.html --self-contained-html \
  --cov=. --cov-branch \
  --cov-report=term \
  --cov-report=html:Tests/evidencias/coverage_html \
  --cov-report=xml:coverage.xml

# --------------------------------------------------------------- frontend ---
paso "2/5  Frontend: Vitest con cobertura (v8) y reporte JSON"
cd "${RAIZ}/frontend"
npx vitest run --coverage
npx vitest run --reporter=json --outputFile=vitest-results.json >/dev/null

# --------------------------------------------------- analisis estatico ------
paso "3/5  Analisis estatico: jscpd (deteccion de codigo duplicado)"
cd "${RAIZ}"
# sin argumento de ruta: se usan las rutas declaradas en .jscpd.json (solo codigo del SUT).
npx jscpd --reporters json,html --output report/jscpd || true   # jscpd sale !=0 sobre el umbral

# ----------------------------------------------------------------- E2E ------
if [[ $CON_E2E -eq 1 ]]; then
  paso "4/5  E2E: Playwright (requiere backend :5000 y frontend :4321 levantados)"
  cd "${RAIZ}/frontend" && npx playwright test
else
  paso "4/5  E2E: OMITIDO (usa --con-e2e con el stack levantado)"
fi

# --------------------------------------------------------------- carga ------
if [[ $CON_CARGA -eq 1 ]]; then
  paso "4b   Carga: Locust 50 usuarios / 2 min contra la BD de PRUEBA (RY-01)"
  cd "${RAIZ}/backend"
  "${RAIZ}/venv/bin/locust" -f Tests/carga/locustfile.py --host http://127.0.0.1:5000 \
    --users 50 --spawn-rate 5 --run-time 2m --headless \
    --html Tests/evidencias/reporte_carga.html --csv Tests/evidencias/carga
fi

# ------------------------------------------------------------- metricas ----
paso "5/5  Calculo automatico de metricas ISO/IEC 25010 + 25023 / 25022"
cd "${RAIZ}"
"$PY" metricas/calcular_metricas.py
ESTADO=$?

printf '\n\033[1;36m==> Evidencias generadas\033[0m\n'
cat <<EOF
  backend/Tests/evidencias/reporte_pytest.html        resultados pytest (HTML)
  backend/Tests/evidencias/coverage_html/index.html   cobertura backend
  backend/Tests/evidencias/junit_backend.xml          resultados pytest (JUnit, para metricas)
  frontend/coverage/index.html                        cobertura frontend
  frontend/tests-e2e/playwright-report/index.html     reporte E2E
  backend/Tests/evidencias/reporte_carga.html         reporte de carga (Locust)
  report/jscpd/jscpd-report.html                      duplicacion de codigo
  metricas/salida/metricas.md                         METRICAS ISO calculadas
EOF

printf '\n\033[1;36m==> Abrir todos los reportes en el navegador\033[0m\n'
echo "  ./metricas/ver_reportes.sh"
exit $ESTADO
