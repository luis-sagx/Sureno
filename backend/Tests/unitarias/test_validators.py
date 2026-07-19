"""DEF-018: validación de email y de identificación (cédula 10d / RUC 13d)."""
from validators import is_valid_cedula, is_valid_email, is_valid_identificacion, is_valid_ruc


# ---------------------- email ----------------------

def test_email_valido():
    assert is_valid_email("cliente@sureno.com") is True


def test_email_sin_arroba_es_invalido():
    assert is_valid_email("clientesureno.com") is False


def test_email_sin_dominio_es_invalido():
    assert is_valid_email("cliente@") is False


def test_email_vacio_es_invalido():
    assert is_valid_email("") is False


# ---------------------- cédula (10 dígitos, módulo 10) ----------------------

def test_cedula_valida():
    assert is_valid_cedula("1710034065") is True


def test_cedula_con_digito_verificador_incorrecto_es_invalida():
    assert is_valid_cedula("1234567890") is False


def test_cedula_con_codigo_provincia_fuera_de_rango_es_invalida():
    assert is_valid_cedula("9910034065") is False


def test_cedula_no_numerica_es_invalida():
    assert is_valid_cedula("asdf") is False


def test_cedula_con_longitud_incorrecta_es_invalida():
    assert is_valid_cedula("123") is False


# ---------------------- RUC (13 dígitos) ----------------------

def test_ruc_persona_natural_valido():
    assert is_valid_ruc("1710034065001") is True


def test_ruc_persona_natural_con_cedula_invalida_es_invalido():
    assert is_valid_ruc("1234567890001") is False


def test_ruc_no_numerico_es_invalido():
    assert is_valid_ruc("123") is False


def test_ruc_con_longitud_incorrecta_es_invalido():
    assert is_valid_ruc("171003406") is False


# ---------------------- identificación (acepta cédula o RUC) ----------------------

def test_identificacion_acepta_cedula_valida():
    assert is_valid_identificacion("1710034065") is True


def test_identificacion_acepta_ruc_valido():
    assert is_valid_identificacion("1710034065001") is True


def test_identificacion_rechaza_formato_arbitrario():
    assert is_valid_identificacion("asdf") is False
    assert is_valid_identificacion("123") is False


def test_identificacion_rechaza_vacio():
    assert is_valid_identificacion("") is False
