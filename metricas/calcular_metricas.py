#!/usr/bin/env python3
"""Calculador automatico de las metricas de calidad del SQAP (SUT: Sureno).

Lee los reportes REALES que generan las herramientas de prueba, aplica las
formulas declaradas en ``umbrales.json`` (cada una asociada a una caracteristica
de ISO/IEC 25010 y a una medida de ISO/IEC 25023 / 25022) y decide
CUMPLE / NO CUMPLE contra el umbral. No hay ningun numero escrito a mano:
si la suite empeora, la tabla del documento cambia.

Fuentes que consume (ver --ayuda-fuentes para el comando que genera cada una):
  backend/Tests/evidencias/junit_backend.xml   pytest  --junitxml
  backend/coverage.xml                         pytest  --cov-report=xml
  frontend/coverage/coverage-summary.json      vitest  --coverage
  frontend/tests-e2e/vitest-results.json       vitest  --reporter=json
  frontend/tests-e2e/report.json               playwright reporter json
  backend/Tests/evidencias/carga_stats.csv     locust  --csv
  report/jscpd/jscpd-report.json               jscpd   --reporters json
  issues.csv                                   export de SonarQube Cloud (ANTES)
  metricas/fuentes.json                        valores declarados (Sonar DESPUES, defectos, KLOC)

Salidas (metricas/salida/):
  metricas.json          resultado completo, apto para CI
  metricas.md            informe legible
  metricas_tabla.tex     tabla lista para \\input{} desde SQAP_Sureno.tex
  trazabilidad_tabla.tex matriz de trazabilidad resuelta contra los reportes

Codigo de salida: 0 si todas las metricas cumplen, 1 si alguna falla o si falta
una fuente obligatoria (usable como Quality Gate propio en CI).

Uso:
    python metricas/calcular_metricas.py
    python metricas/calcular_metricas.py --raiz . --salida metricas/salida
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# --------------------------------------------------------------------------
# Reglas de SonarQube consideradas barreras de accesibilidad
# (ISO/IEC 25010, Usabilidad -> subcaracteristica Accesibilidad).
# --------------------------------------------------------------------------
REGLAS_ACCESIBILIDAD = {
    "Web:InputWithoutLabelCheck",
    "Web:S6853",
    "Web:S6851",
    "Web:S6819",
    "Web:MouseEventWithoutKeyboardEquivalentCheck",
    "Web:FrameWithoutTitleCheck",
}

SEVERIDADES_CRITICAS = {"BLOCKER", "CRITICAL"}
SEVERIDADES_RELEVANTES = {"BLOCKER", "CRITICAL", "MAJOR"}

OPERADORES = {
    ">=": lambda v, u: v >= u,
    "<=": lambda v, u: v <= u,
    "==": lambda v, u: v == u,
    ">": lambda v, u: v > u,
    "<": lambda v, u: v < u,
}


class FuenteFaltante(Exception):
    """Una fuente obligatoria no existe: el calculo no puede continuar."""


# ==========================================================================
# Modelo de resultados
# ==========================================================================
@dataclass
class Resultado:
    id: str
    nombre: str
    iso25010: str
    subcaracteristica: str
    norma_medicion: str
    formula: str
    sustitucion: str          # la formula con los valores reales sustituidos
    valor: float
    unidad: str
    operador: str
    umbral: float
    fuente: str

    @property
    def cumple(self) -> bool:
        return OPERADORES[self.operador](self.valor, self.umbral)

    def fmt_valor(self) -> str:
        return formatear(self.valor, self.unidad)

    def fmt_umbral(self) -> str:
        return formatear(self.umbral, self.unidad)


@dataclass
class CasoTrazado:
    id: str
    titulo: str
    requisitos: list[str]
    iso25010: str
    estado: str               # PASS | FAIL | NO ENCONTRADO
    detalle: list[str] = field(default_factory=list)


def formatear(valor: float, unidad: str) -> str:
    if unidad == "razon":
        return f"{valor * 100:.2f} %"
    if unidad == "ms":
        return f"{valor:.0f} ms"
    if unidad == "s":
        return f"{valor:.1f} s"
    if unidad == "req/s":
        return f"{valor:.2f} req/s"
    if unidad == "def/KLOC":
        return f"{valor:.2f} def/KLOC"
    return f"{valor:g}"


# ==========================================================================
# Lectores de reportes
# ==========================================================================
def leer_json(ruta: Path, comando: str) -> dict:
    if not ruta.exists():
        raise FuenteFaltante(f"No existe {ruta}. Genera la fuente con:\n    {comando}")
    return json.loads(ruta.read_text(encoding="utf-8"))


def leer_junit(ruta: Path) -> dict[str, str]:
    """JUnit XML de pytest -> {nodeid: 'passed'|'failed'|'skipped'}."""
    if not ruta.exists():
        raise FuenteFaltante(
            f"No existe {ruta}. Genera la fuente con:\n"
            "    cd backend && pytest --junitxml=Tests/evidencias/junit_backend.xml"
        )
    estados: dict[str, str] = {}
    for caso in ET.parse(ruta).getroot().iter("testcase"):
        # pytest escribe classname como modulo punteado (Tests.integracion.test_api);
        # se reconstruye el nodeid canonico Tests/integracion/test_api.py::test_x.
        archivo = caso.get("file")
        if not archivo:
            archivo = caso.get("classname", "").replace(".", "/") + ".py"
        nodeid = f"{archivo}::{caso.get('name')}"
        if caso.find("failure") is not None or caso.find("error") is not None:
            estados[nodeid] = "failed"
        elif caso.find("skipped") is not None:
            estados[nodeid] = "skipped"
        else:
            estados[nodeid] = "passed"
    return estados


def leer_cobertura_cobertura_xml(ruta: Path, prefijos_alcance: tuple[str, ...]) -> tuple[int, int]:
    """coverage.xml (formato Cobertura) -> (lineas cubiertas, lineas totales).

    Se limita a los archivos del alcance (app.py, models/, routes/, ...) para no
    inflar la cobertura contando los propios archivos de prueba.
    """
    if not ruta.exists():
        raise FuenteFaltante(
            f"No existe {ruta}. Genera la fuente con:\n"
            "    cd backend && pytest --cov=. --cov-report=xml:coverage.xml"
        )
    cubiertas = totales = 0
    for clase in ET.parse(ruta).getroot().iter("class"):
        nombre = clase.get("filename", "")
        if not nombre.startswith(prefijos_alcance):
            continue
        for linea in clase.iter("line"):
            totales += 1
            if int(linea.get("hits", "0")) > 0:
                cubiertas += 1
    if totales == 0:
        raise FuenteFaltante(
            f"{ruta} no contiene ningun archivo del alcance {prefijos_alcance}."
        )
    return cubiertas, totales


def leer_locust(ruta: Path) -> dict:
    """carga_stats.csv de Locust -> fila agregada."""
    if not ruta.exists():
        raise FuenteFaltante(
            f"No existe {ruta}. Genera la fuente con:\n"
            "    cd backend && locust -f Tests/carga/locustfile.py --host http://127.0.0.1:5000 \\\n"
            "        --users 50 --spawn-rate 5 --run-time 2m --headless --csv Tests/evidencias/carga"
        )
    with ruta.open(encoding="utf-8") as fh:
        filas = list(csv.DictReader(fh))
    agregado = next((f for f in filas if f.get("Name") == "Aggregated"), None)
    if agregado is None:
        raise FuenteFaltante(f"{ruta} no tiene la fila 'Aggregated' de Locust.")
    return agregado


def leer_sonar_antes(ruta: Path) -> dict:
    """Export CSV de SonarQube de la linea base -> conteos por tipo/severidad.

    Acepta el formato sin cabecera (tipo, severidad, componente, linea, mensaje,
    regla) y el formato con cabecera del export nuevo.
    """
    if not ruta.exists():
        raise FuenteFaltante(f"No existe {ruta} (export de SonarQube de la linea base).")
    filas: list[tuple[str, str, str]] = []          # (tipo, severidad, regla)
    with ruta.open(encoding="utf-8") as fh:
        muestra = fh.readline()
        fh.seek(0)
        if muestra.startswith('"Key"') or muestra.startswith("Key,"):
            for r in csv.DictReader(fh):
                filas.append((r["Type"], r["Severity"], r["Rule"]))
        else:
            for r in csv.reader(fh):
                if len(r) >= 6:
                    filas.append((r[0], r[1], r[5]))
    return {
        "total": len(filas),
        "vulnerabilidades": sum(1 for t, _, _ in filas if t == "VULNERABILITY"),
        "bugs": sum(1 for t, _, _ in filas if t == "BUG"),
        "code_smells_total": sum(1 for t, _, _ in filas if t == "CODE_SMELL"),
        "code_smells_critical_major": sum(
            1 for t, s, _ in filas if t == "CODE_SMELL" and s in SEVERIDADES_RELEVANTES
        ),
        "vulnerabilidades_criticas": sum(
            1 for t, s, _ in filas if t == "VULNERABILITY" and s in SEVERIDADES_CRITICAS
        ),
        "issues_accesibilidad": sum(1 for _, _, regla in filas if regla in REGLAS_ACCESIBILIDAD),
    }


def leer_vitest(ruta: Path) -> dict[str, str]:
    """Reporte JSON de Vitest -> {'suite > test': estado}."""
    if not ruta.exists():
        raise FuenteFaltante(
            f"No existe {ruta}. Genera la fuente con:\n"
            "    cd frontend && npx vitest run --reporter=json --outputFile=vitest-results.json"
        )
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    estados: dict[str, str] = {}
    for archivo in datos.get("testResults", []):
        for caso in archivo.get("assertionResults", []):
            titulo = " > ".join(caso.get("ancestorTitles", []) + [caso.get("title", "")])
            estados[titulo] = caso.get("status", "unknown")
    return estados


def leer_playwright(ruta: Path) -> tuple[dict[str, str], dict[str, float]]:
    """Reporte JSON de Playwright -> ({titulo: estado}, {titulo: duracion_s})."""
    if not ruta.exists():
        raise FuenteFaltante(
            f"No existe {ruta}. Levanta backend + frontend y genera la fuente con:\n"
            "    cd frontend && npx playwright test"
        )
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    estados: dict[str, str] = {}
    duraciones: dict[str, float] = {}

    def recorrer(suite: dict) -> None:
        for spec in suite.get("specs", []):
            titulo = spec.get("title", "")
            resultados = [r for t in spec.get("tests", []) for r in t.get("results", [])]
            estados[titulo] = "passed" if spec.get("ok") else "failed"
            duraciones[titulo] = max((r.get("duration", 0) for r in resultados), default=0) / 1000
        for hija in suite.get("suites", []):
            recorrer(hija)

    for suite in datos.get("suites", []):
        recorrer(suite)
    return estados, duraciones


# ==========================================================================
# Trazabilidad: resolver cada CP contra los reportes reales
# ==========================================================================
def resolver_trazabilidad(traza: dict, reportes: dict) -> list[CasoTrazado]:
    casos: list[CasoTrazado] = []
    for caso in traza["casos"]:
        detalle: list[str] = []
        estados: list[str] = []
        for test in caso["tests"]:
            tipo, ref = test["tipo"], test["ref"]
            mapa = reportes.get(tipo)
            if mapa is None:                       # reporte no disponible en esta corrida
                estados.append("no-reporte")
                detalle.append(f"[{tipo}] sin reporte: {ref}")
                continue
            estado = mapa.get(ref)
            if estado is None:
                estados.append("no-encontrado")
                detalle.append(f"[{tipo}] NO ENCONTRADO: {ref}")
            else:
                estados.append(estado)
                detalle.append(f"[{tipo}] {estado}: {ref}")

        if "no-encontrado" in estados:
            resultado = "NO ENCONTRADO"
        elif "failed" in estados:
            resultado = "FAIL"
        elif all(e == "no-reporte" for e in estados):
            resultado = "NO EJECUTADO"
        else:
            resultado = "PASS"

        casos.append(CasoTrazado(
            id=caso["id"], titulo=caso["titulo"], requisitos=caso["requisitos"],
            iso25010=caso["iso25010"], estado=resultado, detalle=detalle,
        ))
    return casos


# ==========================================================================
# Calculo de metricas
# ==========================================================================
def calcular(raiz: Path) -> tuple[list[Resultado], list[CasoTrazado], dict, list[str]]:
    avisos: list[str] = []
    umbrales = {m["id"]: m for m in leer_json(raiz / "metricas/umbrales.json", "n/a")["metricas"]}
    fuentes = leer_json(raiz / "metricas/fuentes.json", "n/a")
    traza = leer_json(raiz / "metricas/trazabilidad.json", "n/a")

    # --- Reportes obligatorios -------------------------------------------
    junit = leer_junit(raiz / "backend/Tests/evidencias/junit_backend.xml")
    cob_be = leer_cobertura_cobertura_xml(
        raiz / "backend/coverage.xml",
        ("app.py", "validators.py", "db_indexes.py", "models/", "routes/", "config.py"),
    )
    cob_fe = leer_json(
        raiz / "frontend/coverage/coverage-summary.json",
        "cd frontend && npx vitest run --coverage",
    )["total"]["lines"]
    vitest = leer_vitest(raiz / "frontend/vitest-results.json")
    jscpd = leer_json(
        raiz / "report/jscpd/jscpd-report.json",
        "npx jscpd --reporters json,html --output report/jscpd .",
    )["statistics"]["total"]
    sonar_antes = leer_sonar_antes(raiz / fuentes["sonar_antes_csv"])
    sonar_desp = fuentes["sonar_despues"]

    # --- Reportes opcionales (requieren el stack levantado) --------------
    try:
        locust = leer_locust(raiz / "backend/Tests/evidencias/carga_stats.csv")
    except FuenteFaltante as exc:
        locust, avisos = None, avisos + [str(exc)]
    try:
        pw_estados, pw_duraciones = leer_playwright(raiz / "frontend/tests-e2e/report.json")
    except FuenteFaltante as exc:
        pw_estados, pw_duraciones = None, {}
        avisos.append(str(exc))

    reportes = {"pytest": junit, "vitest": vitest, "playwright": pw_estados}
    casos = resolver_trazabilidad(traza, reportes)

    res: list[Resultado] = []

    def add(mid: str, valor: float, sustitucion: str, fuente: str) -> None:
        d = umbrales[mid]
        res.append(Resultado(
            id=d["id"], nombre=d["nombre"], iso25010=d["iso25010"],
            subcaracteristica=d["subcaracteristica"], norma_medicion=d["norma_medicion"],
            formula=d["formula"], sustitucion=sustitucion, valor=valor,
            unidad=d["unidad"], operador=d["operador"], umbral=d["umbral"], fuente=fuente,
        ))

    # ---- MC-01 Completitud funcional: requisitos cubiertos ---------------
    reqs = set(traza["requisitos"])
    reqs_ok = {r for c in casos if c.estado == "PASS" for r in c.requisitos}
    add("MC-01", len(reqs_ok) / len(reqs),
        f"X = {len(reqs_ok)} / {len(reqs)}",
        "trazabilidad.json resuelta contra JUnit/Vitest/Playwright")

    # ---- MC-02 Correccion funcional: casos CP pasados --------------------
    ejecutados = [c for c in casos if c.estado in {"PASS", "FAIL"}]
    pasados = [c for c in ejecutados if c.estado == "PASS"]
    add("MC-02", len(pasados) / len(ejecutados) if ejecutados else 0.0,
        f"X = {len(pasados)} / {len(ejecutados)}",
        "casos CP-01..CP-24 de la matriz de trazabilidad")

    # ---- MC-03 Densidad de fallos de la suite ---------------------------
    total_tests = len(junit) + len(vitest) + (len(pw_estados) if pw_estados else 0)
    fallos = (
        sum(1 for e in junit.values() if e == "failed")
        + sum(1 for e in vitest.values() if e == "failed")
        + (sum(1 for e in pw_estados.values() if e == "failed") if pw_estados else 0)
    )
    add("MC-03", fallos / total_tests,
        f"X = {fallos} / {total_tests}",
        "junit_backend.xml + vitest-results.json"
        + (" + report.json (Playwright)" if pw_estados else ""))

    # ---- MC-04 Densidad de defectos abiertos ----------------------------
    abiertos = fuentes["defectos"]["abiertos_al_cierre"]
    kloc = fuentes["alcance_codigo"]["kloc"]
    add("MC-04", abiertos / kloc, f"X = {abiertos} / {kloc:.3f} KLOC",
        "GitHub Issues (fuentes.json) + conteo de lineas del alcance")

    # ---- MC-05/06/07 Carga (Locust) -------------------------------------
    if locust is not None:
        n = int(locust["Request Count"])
        f_ = int(locust["Failure Count"])
        p95 = float(locust["95%"])
        rps = float(locust["Requests/s"])
        add("MC-05", (n - f_) / n, f"X = ({n} - {f_}) / {n}", "carga_stats.csv (Aggregated)")
        add("MC-06", p95, f"X = p95 = {p95:.0f} ms", "carga_stats.csv (Aggregated)")
        add("MC-07", rps, f"X = {n} / {fuentes['carga']['duracion_segundos']} s = {rps:.2f} req/s",
            "carga_stats.csv (Aggregated)")

    # ---- MC-08/09 Seguridad ---------------------------------------------
    v_ant = sonar_antes["vulnerabilidades"]
    v_des = sonar_desp["vulnerabilidades"]
    add("MC-08", float(v_des), f"X = {v_des} (BLOCKER+CRITICAL abiertas)",
        "dashboard SonarQube Cloud DESPUES (fuentes.json)")
    add("MC-09", (v_ant - v_des) / v_ant, f"X = ({v_ant} - {v_des}) / {v_ant}",
        "issues.csv (ANTES) vs dashboard SonarQube (DESPUES)")

    # ---- MC-10/11 Cobertura ---------------------------------------------
    cub, tot = cob_be
    add("MC-10", cub / tot, f"X = {cub} / {tot} lineas", "backend/coverage.xml")
    add("MC-11", cob_fe["pct"] / 100,
        f"X = {cob_fe['covered']} / {cob_fe['total']} lineas",
        "frontend/coverage/coverage-summary.json")

    # ---- MC-12 Duplicacion ----------------------------------------------
    add("MC-12", jscpd["duplicatedLines"] / jscpd["lines"],
        f"X = {jscpd['duplicatedLines']} / {jscpd['lines']} lineas",
        "report/jscpd/jscpd-report.json")

    # ---- MC-13 Reduccion de code smells ---------------------------------
    s_ant = sonar_antes["code_smells_critical_major"]
    s_des = sonar_desp["code_smells_critical_major"]
    add("MC-13", (s_ant - s_des) / s_ant, f"X = ({s_ant} - {s_des}) / {s_ant}",
        "issues.csv (ANTES) vs dashboard SonarQube (DESPUES)")

    # ---- MC-14 Accesibilidad --------------------------------------------
    a_des = sonar_desp["issues_accesibilidad"]
    add("MC-14", float(a_des),
        f"X = {a_des} (ANTES: {sonar_antes['issues_accesibilidad']})",
        "reglas Web:* de accesibilidad en SonarQube")

    # ---- MC-15/16 Calidad en uso (ISO 25022) ----------------------------
    tareas = [c for c in casos if traza_es_tarea(traza, c.id)]
    if pw_estados is not None:
        completadas = sum(1 for c in tareas if c.estado == "PASS")
        add("MC-15", completadas / len(tareas) if tareas else 0.0,
            f"X = {completadas} / {len(tareas)} tareas E2E",
            "report.json (Playwright)")
        t_compra = pw_duraciones.get("agregar producto al carrito y completar checkout")
        if t_compra is not None:
            add("MC-16", t_compra, f"X = {t_compra:.1f} s (recorrido completo de compra)",
                "report.json (Playwright, duracion del spec)")

    contexto = {
        "sonar_antes": sonar_antes, "sonar_despues": sonar_desp,
        "jscpd": jscpd, "kloc": kloc,
        "tests": {"backend": len(junit), "frontend": len(vitest),
                  "e2e": len(pw_estados) if pw_estados else 0},
        "defectos": fuentes["defectos"],
    }
    return res, casos, contexto, avisos


def traza_es_tarea(traza: dict, cid: str) -> bool:
    for c in traza["casos"]:
        if c["id"] == cid:
            return bool(c.get("tarea_calidad_en_uso")) or any(
                t["tipo"] == "playwright" for t in c["tests"]
            )
    return False


# ==========================================================================
# Salidas
# ==========================================================================
VERDE, ROJO, GRIS, RESET = "\033[32m", "\033[31m", "\033[90m", "\033[0m"


def imprimir_consola(res: list[Resultado], casos: list[CasoTrazado],
                     ctx: dict, avisos: list[str]) -> None:
    print(f"\n{'=' * 100}")
    print("  METRICAS DE CALIDAD - SQAP Sureno   |   Norma aplicada: ISO/IEC 25010")
    print("  Formulas segun ISO/IEC 25023 (producto) y 25022 (calidad en uso), familia SQuaRE")
    print(f"  Calculado: {datetime.now():%Y-%m-%d %H:%M:%S}")
    print("=" * 100)
    print(f"{'ID':<7}{'Metrica':<38}{'Formula aplicada':<28}{'Valor':>12}  {'Umbral':>12}  Estado")
    print("-" * 100)
    for r in res:
        color = VERDE if r.cumple else ROJO
        icono = "CUMPLE" if r.cumple else "NO CUMPLE"
        print(f"{r.id:<7}{r.nombre[:37]:<38}{r.sustitucion[:27]:<28}"
              f"{r.fmt_valor():>12}  {r.operador} {r.fmt_umbral():>10}  {color}{icono}{RESET}")
    print("-" * 100)

    fallidas = [r for r in res if not r.cumple]
    trazas_mal = [c for c in casos if c.estado not in {"PASS", "NO EJECUTADO"}]
    print(f"Metricas evaluadas: {len(res)} | cumplen: {len(res) - len(fallidas)} | "
          f"fallan: {len(fallidas)}")
    print(f"Casos de prueba trazados: {len(casos)} | "
          f"PASS: {sum(1 for c in casos if c.estado == 'PASS')} | "
          f"FAIL: {sum(1 for c in casos if c.estado == 'FAIL')} | "
          f"NO ENCONTRADO: {sum(1 for c in casos if c.estado == 'NO ENCONTRADO')} | "
          f"NO EJECUTADO: {sum(1 for c in casos if c.estado == 'NO EJECUTADO')}")
    print(f"Pruebas automatizadas: backend {ctx['tests']['backend']} | "
          f"frontend {ctx['tests']['frontend']} | E2E {ctx['tests']['e2e']}")

    for c in trazas_mal:
        print(f"  {ROJO}{c.id} {c.estado}{RESET}: " + "; ".join(c.detalle))
    for a in avisos:
        print(f"{GRIS}[aviso] {a.splitlines()[0]}{RESET}")

    veredicto = "APTO" if not fallidas and not trazas_mal else "NO APTO"
    color = VERDE if veredicto == "APTO" else ROJO
    print(f"\nVEREDICTO AUTOMATICO (criterios de salida del SQAP): {color}{veredicto}{RESET}\n")


def escribir_markdown(ruta: Path, res: list[Resultado], casos: list[CasoTrazado],
                      ctx: dict, avisos: list[str]) -> None:
    L = [
        "# Metricas de calidad - SQAP Sureno",
        "",
        f"Generado automaticamente por `metricas/calcular_metricas.py` el "
        f"{datetime.now():%Y-%m-%d %H:%M}.",
        "",
        "Norma aplicada: **ISO/IEC 25010** (modelo de calidad del producto). Las formulas "
        "toman su forma de **ISO/IEC 25023** (calidad del producto) y **ISO/IEC 25022** "
        "(calidad en uso), partes de la misma familia SQuaRE.",
        "",
        "## 1. Resultados",
        "",
        "| ID | Caracteristica ISO 25010 | Metrica | Formula | Sustitucion | Valor | Umbral | Estado |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in res:
        L.append(
            f"| {r.id} | {r.iso25010} / {r.subcaracteristica} | {r.nombre} | `{r.formula}` | "
            f"`{r.sustitucion}` | **{r.fmt_valor()}** | {r.operador} {r.fmt_umbral()} | "
            f"{'CUMPLE' if r.cumple else 'NO CUMPLE'} |"
        )
    L += ["", "## 2. Trazabilidad requisito -> caso -> prueba automatizada", "",
          "| CP | Titulo | Requisitos | Caracteristica ISO 25010 | Estado | Pruebas que lo implementan |",
          "|---|---|---|---|---|---|"]
    for c in casos:
        L.append(f"| {c.id} | {c.titulo} | {', '.join(c.requisitos)} | {c.iso25010} | "
                 f"{c.estado} | {'<br>'.join(c.detalle)} |")

    fallidas = [r for r in res if not r.cumple]
    L += ["", "## 3. Veredicto", "",
          f"- Metricas que cumplen: **{len(res) - len(fallidas)}/{len(res)}**",
          f"- Casos de prueba PASS: **{sum(1 for c in casos if c.estado == 'PASS')}/{len(casos)}**",
          f"- Pruebas automatizadas ejecutadas: backend {ctx['tests']['backend']}, "
          f"frontend {ctx['tests']['frontend']}, E2E {ctx['tests']['e2e']}",
          "",
          f"**Veredicto automatico: {'APTO' if not fallidas else 'NO APTO'}** "
          "(criterios de salida del SQAP, seccion 5.2).",
          ]
    if avisos:
        L += ["", "## 4. Avisos (fuentes no disponibles en esta corrida)", ""]
        L += [f"- {a.splitlines()[0]}" for a in avisos]
    ruta.write_text("\n".join(L) + "\n", encoding="utf-8")


def tex_escape(texto: str) -> str:
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("_", r"\_"),
                 ("#", r"\#"), ("$", r"\$"), ("{", r"\{"), ("}", r"\}")):
        texto = texto.replace(a, b)
    return texto


OPERADOR_TEX = {">=": r"\geq", "<=": r"\leq", "==": "=", ">": ">", "<": "<"}


def escribir_tex_metricas(ruta: Path, res: list[Resultado]) -> None:
    L = [
        "% Generado automaticamente por metricas/calcular_metricas.py -- NO editar a mano.",
        r"\begin{longtable}{p{0.9cm}p{3.1cm}p{2.6cm}p{3.2cm}p{1.8cm}p{1.6cm}p{1.5cm}}",
        r"\toprule",
        r"\textbf{ID} & \textbf{M\'etrica (ISO 25010)} & \textbf{F\'ormula} & "
        r"\textbf{Sustituci\'on} & \textbf{Valor} & \textbf{Umbral} & \textbf{Estado} \\",
        r"\midrule", r"\endhead",
    ]
    for r in res:
        estado = (r"\textcolor{cumple}{\textbf{CUMPLE}}" if r.cumple
                  else r"\textcolor{blocker}{\textbf{NO CUMPLE}}")
        L.append(
            f"{r.id} & {tex_escape(r.nombre)} \\newline "
            f"\\textit{{\\small {tex_escape(r.iso25010)}}} & "
            f"$ {tex_escape(r.formula)} $ & {tex_escape(r.sustitucion)} & "
            f"\\textbf{{{tex_escape(r.fmt_valor())}}} & "
            f"${OPERADOR_TEX[r.operador]}$ {tex_escape(r.fmt_umbral())} & {estado} \\\\"
        )
    L += [r"\bottomrule", r"\end{longtable}"]
    ruta.write_text("\n".join(L) + "\n", encoding="utf-8")


def escribir_tex_trazabilidad(ruta: Path, casos: list[CasoTrazado]) -> None:
    L = [
        "% Generado automaticamente por metricas/calcular_metricas.py -- NO editar a mano.",
        r"\begin{longtable}{p{1.2cm}p{4.6cm}p{1.9cm}p{4.2cm}p{1.6cm}p{1.1cm}}",
        r"\toprule",
        r"\textbf{CP} & \textbf{T\'itulo} & \textbf{Req.} & "
        r"\textbf{ISO/IEC 25010} & \textbf{Pruebas} & \textbf{Estado} \\",
        r"\midrule", r"\endhead",
    ]
    for c in casos:
        estado = (r"\textcolor{cumple}{PASS}" if c.estado == "PASS"
                  else rf"\textcolor{{blocker}}{{{c.estado}}}")
        tipos: dict[str, int] = {}
        for d in c.detalle:
            tipo = d.split("]")[0].lstrip("[")
            tipos[tipo] = tipos.get(tipo, 0) + 1
        resumen = ", ".join(f"{n}~{t}" for t, n in tipos.items())
        L.append(f"{c.id} & {tex_escape(c.titulo)} & {tex_escape(', '.join(c.requisitos))} & "
                 f"{tex_escape(c.iso25010)} & {tex_escape(resumen)} & {estado} \\\\")
    L += [r"\bottomrule", r"\end{longtable}"]
    ruta.write_text("\n".join(L) + "\n", encoding="utf-8")


def escribir_json(ruta: Path, res: list[Resultado], casos: list[CasoTrazado],
                  ctx: dict, avisos: list[str]) -> None:
    ruta.write_text(json.dumps({
        "generado": datetime.now().isoformat(timespec="seconds"),
        "norma_aplicada": "ISO/IEC 25010",
        "normas_de_medicion": ["ISO/IEC 25023", "ISO/IEC 25022"],
        "metricas": [
            {"id": r.id, "nombre": r.nombre, "iso25010": r.iso25010,
             "subcaracteristica": r.subcaracteristica, "norma_medicion": r.norma_medicion,
             "formula": r.formula, "sustitucion": r.sustitucion, "valor": r.valor,
             "unidad": r.unidad, "operador": r.operador, "umbral": r.umbral,
             "cumple": r.cumple, "fuente": r.fuente}
            for r in res
        ],
        "trazabilidad": [
            {"id": c.id, "titulo": c.titulo, "requisitos": c.requisitos,
             "iso25010": c.iso25010, "estado": c.estado, "pruebas": c.detalle}
            for c in casos
        ],
        "contexto": ctx,
        "avisos": [a.splitlines()[0] for a in avisos],
        "veredicto": "APTO" if all(r.cumple for r in res) else "NO APTO",
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# ==========================================================================
def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--raiz", default=Path(__file__).resolve().parent.parent, type=Path,
                   help="raiz del repositorio (por defecto, la del script)")
    p.add_argument("--salida", default=None, type=Path,
                   help="directorio de salida (por defecto metricas/salida)")
    p.add_argument("--estricto", action="store_true",
                   help="falla tambien si faltan fuentes opcionales (carga / E2E)")
    args = p.parse_args()

    raiz: Path = args.raiz
    salida: Path = args.salida or (raiz / "metricas/salida")
    salida.mkdir(parents=True, exist_ok=True)

    try:
        res, casos, ctx, avisos = calcular(raiz)
    except FuenteFaltante as exc:
        print(f"{ROJO}ERROR: fuente obligatoria no disponible.{RESET}\n{exc}", file=sys.stderr)
        return 1

    imprimir_consola(res, casos, ctx, avisos)
    escribir_json(salida / "metricas.json", res, casos, ctx, avisos)
    escribir_markdown(salida / "metricas.md", res, casos, ctx, avisos)
    escribir_tex_metricas(salida / "metricas_tabla.tex", res)
    escribir_tex_trazabilidad(salida / "trazabilidad_tabla.tex", casos)
    print(f"Reportes escritos en {salida}/ "
          "(metricas.json, metricas.md, metricas_tabla.tex, trazabilidad_tabla.tex)")

    fallo = (any(not r.cumple for r in res)
             or any(c.estado in {"FAIL", "NO ENCONTRADO"} for c in casos)
             or (args.estricto and avisos))
    return 1 if fallo else 0


if __name__ == "__main__":
    raise SystemExit(main())
