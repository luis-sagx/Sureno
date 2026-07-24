#!/usr/bin/env bash
# Verifica que todos los reportes de evidencia existen, no estan vacios y son
# recientes; opcionalmente los abre en el navegador.
#
#   ./metricas/ver_reportes.sh            # solo verificar
#   ./metricas/ver_reportes.sh --abrir    # verificar y abrir en el navegador
#
# Un reporte se marca ANTIGUO si tiene mas de 24 h: probablemente no corresponde
# a la ultima ejecucion de la suite y no deberia usarse como evidencia.
set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ABRIR=0
[[ "${1:-}" == "--abrir" ]] && ABRIR=1

VERDE='\033[32m'; ROJO='\033[31m'; AMAR='\033[33m'; CIAN='\033[1;36m'; NC='\033[0m'

# ruta|descripcion|comando que lo genera|criterio de calidad
REPORTES=(
"backend/Tests/evidencias/reporte_pytest.html|Resultados pytest (164 pruebas)|pytest --html=...|calidad: 164/164 pruebas PASS"
"backend/Tests/evidencias/coverage_html/index.html|Cobertura backend (94.5%)|pytest --cov-report=html:...|calidad: cobertura backend >= 80%"
"frontend/coverage/index.html|Cobertura frontend (100%)|npx vitest run --coverage|calidad: cobertura frontend >= 80%"
"frontend/tests-e2e/playwright-report/index.html|Reporte E2E (18 pruebas)|npx playwright test|calidad: 18/18 E2E PASS"
"backend/Tests/evidencias/reporte_carga.html|Carga Locust (50 usuarios)|locust ... --html=...|calidad: disponibilidad >= 99%, p95 <= 800 ms, capacidad >= 20 req/s"
"report/jscpd/jscpd-report.html|Duplicacion de codigo (1.23%)|npx jscpd --reporters json,html|calidad: duplicacion <= 3%"
"metricas/salida/metricas.md|METRICAS ISO calculadas (16/16)|python metricas/calcular_metricas.py|calidad: 16/16 metricas CUMPLEN"
)

printf "\n${CIAN}Verificacion de reportes de evidencia — SQAP Sureno${NC}\n"
printf '%.0s─' {1..120}; printf '\n'

FALTAN=0; ANTIGUOS=0; AHORA=$(date +%s)

for entrada in "${REPORTES[@]}"; do
  IFS='|' read -r ruta desc comando criterio <<< "$entrada"
  abs="${RAIZ}/${ruta}"

  if [[ ! -f "$abs" ]]; then
    printf "${ROJO}FALTA  ${NC} %-48s %s (%s)\n" "$desc" "$ruta" "$criterio"
    printf "        ${AMAR}genera con:${NC} %s\n" "$comando"
    ((FALTAN++)); continue
  fi

  tam=$(stat -c%s "$abs")
  mod=$(stat -c%Y "$abs")
  edad_h=$(( (AHORA - mod) / 3600 ))

  if (( tam == 0 )); then
    printf "${ROJO}VACIO  ${NC} %-48s %s (%s)\n" "$desc" "$ruta" "$criterio"
    ((FALTAN++)); continue
  fi

  if (( edad_h > 24 )); then
    printf "${AMAR}ANTIGUO${NC} %-48s %s (%s; %s h)\n" "$desc" "$ruta" "$criterio" "$edad_h"
    ((ANTIGUOS++))
  else
    printf "${VERDE}OK     ${NC} %-48s %s (%s; hace %s h)\n" "$desc" "$ruta" "$criterio" "$edad_h"
  fi
done

printf '%.0s─' {1..120}; printf '\n'

if (( FALTAN > 0 )); then
  printf "${ROJO}%d reporte(s) faltan o estan vacios.${NC} Ejecuta: ./metricas/ejecutar_suite.sh --todo\n\n" "$FALTAN"
elif (( ANTIGUOS > 0 )); then
  printf "${AMAR}%d reporte(s) tienen mas de 24 h.${NC} Regenera antes de grabar o exponer.\n\n" "$ANTIGUOS"
else
  printf "${VERDE}Todos los reportes presentes y recientes.${NC}\n\n"
fi

if (( ABRIR == 1 )); then
  printf "${CIAN}Abriendo en el navegador...${NC}\n"
  for entrada in "${REPORTES[@]}"; do
    IFS='|' read -r ruta _ _ _ <<< "$entrada"
    [[ -f "${RAIZ}/${ruta}" && "$ruta" == *.html ]] && xdg-open "${RAIZ}/${ruta}" >/dev/null 2>&1
  done
fi

exit $(( FALTAN > 0 ? 1 : 0 ))
