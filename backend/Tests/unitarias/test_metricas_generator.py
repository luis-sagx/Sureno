import importlib.util
import sys
from pathlib import Path


def cargar_calculador():
    raiz = Path(__file__).resolve().parents[3]
    ruta = raiz / "metricas" / "calcular_metricas.py"
    spec = importlib.util.spec_from_file_location("calcular_metricas", ruta)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = modulo
    spec.loader.exec_module(modulo)
    return modulo


def resultado_ok(modulo):
    return modulo.Resultado(
        id="MC-01",
        nombre="Completitud funcional",
        iso25010="Adecuacion funcional",
        subcaracteristica="Completitud",
        norma_medicion="ISO/IEC 25023",
        formula="X = A / B",
        sustitucion="X = 1 / 1",
        valor=1.0,
        unidad="razon",
        operador=">=",
        umbral=1.0,
        fuente="test",
    )


def test_cli_por_defecto_solo_escribe_markdown(tmp_path, monkeypatch):
    modulo = cargar_calculador()

    monkeypatch.setattr(
        sys,
        "argv",
        ["calcular_metricas.py", "--raiz", str(tmp_path), "--salida", str(tmp_path / "salida")],
    )
    monkeypatch.setattr(modulo, "calcular", lambda raiz: ([resultado_ok(modulo)], [], {}, []))
    monkeypatch.setattr(modulo, "imprimir_consola", lambda *args: None)
    monkeypatch.setattr(modulo, "escribir_markdown", lambda ruta, *args: ruta.write_text("# ok\n", encoding="utf-8"))
    monkeypatch.setattr(
        modulo,
        "escribir_json",
        lambda *args: (_ for _ in ()).throw(AssertionError("no debe escribir JSON por defecto")),
        raising=False,
    )
    monkeypatch.setattr(
        modulo,
        "escribir_tex_metricas",
        lambda *args: (_ for _ in ()).throw(AssertionError("no debe escribir LaTeX por defecto")),
        raising=False,
    )
    monkeypatch.setattr(
        modulo,
        "escribir_tex_trazabilidad",
        lambda *args: (_ for _ in ()).throw(AssertionError("no debe escribir LaTeX por defecto")),
        raising=False,
    )

    assert modulo.main() == 0
    assert (tmp_path / "salida" / "metricas.md").exists()


def test_calcular_usa_sonar_antes_de_fuentes_json_sin_issues_csv(tmp_path, monkeypatch):
    modulo = cargar_calculador()

    fuentes = {
        "sonar_antes": {
            "total": 111,
            "vulnerabilidades": 33,
            "bugs": 30,
            "code_smells_total": 48,
            "code_smells_critical_major": 42,
            "vulnerabilidades_criticas": 2,
            "issues_accesibilidad": 52,
        },
        "sonar_despues": {
            "vulnerabilidades": 0,
            "bugs": 0,
            "code_smells_critical_major": 4,
            "code_smells_total": 4,
            "issues_accesibilidad": 0,
        },
        "defectos": {"abiertos_al_cierre": 0},
        "alcance_codigo": {"kloc": 1.0},
        "carga": {"duracion_segundos": 120},
    }
    umbrales = {
        "metricas": [
            {
                "id": f"MC-{i:02d}",
                "nombre": f"Metrica {i}",
                "iso25010": "ISO",
                "subcaracteristica": "Sub",
                "norma_medicion": "Norma",
                "formula": "X",
                "unidad": "razon",
                "operador": ">=",
                "umbral": 0,
            }
            for i in range(1, 17)
        ]
    }
    traza = {
        "requisitos": ["RF-01"],
        "casos": [
            {
                "id": "CP-01",
                "titulo": "Caso",
                "requisitos": ["RF-01"],
                "iso25010": "Adecuacion funcional",
                "tests": [{"tipo": "pytest", "ref": "test_ok"}],
            }
        ],
    }

    def fake_leer_json(ruta, *_args):
        nombre = str(ruta)
        if nombre.endswith("umbrales.json"):
            return umbrales
        if nombre.endswith("fuentes.json"):
            return fuentes
        if nombre.endswith("trazabilidad.json"):
            return traza
        if nombre.endswith("coverage-summary.json"):
            return {"total": {"lines": {"pct": 100, "covered": 1, "total": 1}}}
        if nombre.endswith("jscpd-report.json"):
            return {"statistics": {"total": {"duplicatedLines": 0, "lines": 10}}}
        raise AssertionError(nombre)

    monkeypatch.setattr(modulo, "leer_json", fake_leer_json)
    monkeypatch.setattr(modulo, "leer_junit", lambda *_: {"test_ok": "passed"})
    monkeypatch.setattr(modulo, "leer_cobertura_cobertura_xml", lambda *_: (1, 1))
    monkeypatch.setattr(modulo, "leer_vitest", lambda *_: {})
    monkeypatch.setattr(modulo, "leer_locust", lambda *_: None)
    monkeypatch.setattr(modulo, "leer_playwright", lambda *_: (None, {}))
    monkeypatch.setattr(
        modulo,
        "leer_sonar_antes",
        lambda *_: (_ for _ in ()).throw(AssertionError("no debe leer issues.csv")),
    )

    res, _casos, ctx, _avisos = modulo.calcular(tmp_path)

    assert ctx["sonar_antes"]["vulnerabilidades"] == 33
    assert next(r for r in res if r.id == "MC-09").sustitucion == "X = (33 - 0) / 33"
