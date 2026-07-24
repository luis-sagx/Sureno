# Métricas de calidad — SQAP Sureño

Motor de cálculo automático de las métricas de calidad del SUT.

**Norma aplicada: ISO/IEC 25010** (modelo de calidad del producto). Es la única norma
que el proyecto adopta: define *qué* característica evalúa cada métrica.

Las fórmulas toman su forma de dos partes de la **misma familia SQuaRE**, que son el
instrumento de medición de 25010 —no un marco adicional:

| Parte de SQuaRE | Rol |
|---|---|
| **ISO/IEC 25023** | Medidas de calidad del producto: forma de MC-01…MC-14. |
| **ISO/IEC 25022** | Medidas de calidad **en uso**: MC-15 (*task completion*) y MC-16 (*task time*). |

Ningún número del documento SQAP se escribe a mano: las tablas del PDF se generan
desde aquí (`salida/*.tex`, incluidas con `\input`).

## Ejecutar

```bash
# Todo de una vez (suite completa + métricas). Es el comando de la exposición.
./metricas/ejecutar_suite.sh --todo

# Solo el cálculo, si los reportes ya existen
python metricas/calcular_metricas.py
```

`--con-e2e` y `--con-carga` requieren el stack levantado:

```bash
cd backend  && source ../venv/bin/activate && python app.py   # :5000
cd frontend && npm run dev                                    # :4321
```

Código de salida: **0** = todas las métricas cumplen · **1** = alguna incumple, o
algún caso de prueba de la matriz quedó en `FAIL` / `NO ENCONTRADO`. Sirve como
*quality gate* propio en CI.

## Archivos

| Archivo | Qué contiene |
|---|---|
| `umbrales.json` | Definición formal de las 16 métricas: norma, fórmula, unidad, operador, umbral. **Cambiar un umbral aquí cambia el veredicto** del documento y de CI. |
| `trazabilidad.json` | Matriz de trazabilidad *ejecutable*: cada CP-xx declara los nodeids exactos de las pruebas que lo implementan. |
| `fuentes.json` | Valores que no se derivan de la suite local (dashboard SonarQube DESPUÉS, defectos abiertos, KLOC), cada uno con su procedencia declarada. |
| `calcular_metricas.py` | Motor: parsea reportes → aplica fórmulas → CUMPLE / NO CUMPLE. |
| `ejecutar_suite.sh` | Corre pytest, Vitest, Playwright, Locust y jscpd, y después el cálculo. |
| `salida/metricas.json` | Resultado completo, consumible por CI. |
| `salida/metricas.md` | Informe legible con la fórmula, la sustitución de valores y el veredicto. |
| `salida/metricas_tabla.tex` | Tabla que el SQAP incluye en el Informe de cierre. |
| `salida/trazabilidad_tabla.tex` | Matriz resuelta que el SQAP incluye en el diseño de casos. |

## De dónde salen los datos

| Fuente | Comando que la genera | Métricas que alimenta |
|---|---|---|
| `backend/Tests/evidencias/junit_backend.xml` | `pytest --junitxml=...` | MC-01, MC-02, MC-03 |
| `backend/coverage.xml` | `pytest --cov-report=xml` | MC-10 |
| `frontend/coverage/coverage-summary.json` | `npx vitest run --coverage` | MC-11 |
| `frontend/vitest-results.json` | `npx vitest run --reporter=json` | MC-01, MC-02, MC-03 |
| `frontend/tests-e2e/report.json` | `npx playwright test` | MC-02, MC-15, MC-16 |
| `backend/Tests/evidencias/carga_stats.csv` | `locust --headless --csv` | MC-05, MC-06, MC-07 |
| `report/jscpd/jscpd-report.json` | `npx jscpd --reporters json,html` | MC-12 |
| `issues.csv` | export de SonarQube Cloud (línea base) | MC-09, MC-13, MC-14 |
| `metricas/fuentes.json` | dashboard SonarQube DESPUÉS + GitHub Issues | MC-04, MC-08, MC-09, MC-13, MC-14 |

Si falta una fuente **obligatoria**, el script aborta indicando el comando exacto que
la genera. Si falta una **opcional** (carga o E2E, que necesitan el stack levantado),
avisa y omite las métricas que dependen de ella; con `--estricto` eso también falla.

## Verificar que las métricas son reales

1. `metricas/umbrales.json` → cada métrica declara norma, fórmula y umbral.
2. `metricas/calcular_metricas.py` → cada fórmula está implementada sobre valores
   leídos del reporte correspondiente; no hay constantes escritas a mano.
3. `metricas/salida/metricas.md` → columna *Sustitución*, con los valores reales
   dentro de la fórmula (p. ej. MC-09: `X = (33 - 0) / 33`).
4. Subir un umbral o comentar una prueba y volver a ejecutar: el veredicto cambia.

## Añadir una métrica

1. Añadir la entrada en `umbrales.json` (id, ISO 25010, norma de medición, fórmula, unidad, operador, umbral).
2. En `calcular_metricas.py`, dentro de `calcular()`, llamar a `add("MC-xx", valor, sustitucion, fuente)`
   con el valor derivado del reporte correspondiente.
3. Ejecutar; la tabla del SQAP se regenera sola.
