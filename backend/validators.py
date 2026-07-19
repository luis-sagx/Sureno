"""DEF-018: validación de email e identificación (cédula 10d / RUC 13d, Ecuador)."""


def is_valid_email(email):
    if not email or any(c.isspace() for c in email):
        return False
    local, sep, domain = email.partition("@")
    if sep != "@" or not local or not domain:
        return False
    if domain.startswith(".") or domain.endswith("."):
        return False
    return "." in domain


def is_valid_cedula(cedula):
    if not cedula or not cedula.isdigit() or len(cedula) != 10:
        return False
    provincia = int(cedula[0:2])
    if provincia < 1 or provincia > 24:
        return False
    if int(cedula[2]) >= 6:
        return False
    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    suma = 0
    for i, coef in enumerate(coeficientes):
        valor = int(cedula[i]) * coef
        if valor > 9:
            valor -= 9
        suma += valor
    modulo = suma % 10
    verificador = 0 if modulo == 0 else 10 - modulo
    return verificador == int(cedula[9])


def _validar_ruc_natural(ruc):
    if not is_valid_cedula(ruc[0:10]):
        return False
    return int(ruc[10:13]) >= 1


def _validar_ruc_publico(ruc):
    if ruc[2] != "6":
        return False
    coeficientes = [3, 2, 7, 6, 5, 4, 3, 2]
    suma = sum(int(ruc[i]) * coeficientes[i] for i in range(8))
    modulo = suma % 11
    verificador = 0 if modulo == 0 else 11 - modulo
    if verificador == 10 or verificador != int(ruc[8]):
        return False
    return ruc[9:] == "0001"


def _validar_ruc_juridico(ruc):
    if ruc[2] != "9":
        return False
    coeficientes = [4, 3, 2, 7, 6, 5, 4, 3, 2]
    suma = sum(int(ruc[i]) * coeficientes[i] for i in range(9))
    modulo = suma % 11
    verificador = 0 if modulo == 0 else 11 - modulo
    if verificador == 10 or verificador != int(ruc[9]):
        return False
    return int(ruc[10:13]) >= 1


def is_valid_ruc(ruc):
    if not ruc or not ruc.isdigit() or len(ruc) != 13:
        return False
    provincia = int(ruc[0:2])
    if provincia < 1 or provincia > 24:
        return False
    tercer_digito = int(ruc[2])
    if tercer_digito < 6:
        return _validar_ruc_natural(ruc)
    if tercer_digito == 6:
        return _validar_ruc_publico(ruc)
    if tercer_digito == 9:
        return _validar_ruc_juridico(ruc)
    return False


def is_valid_identificacion(valor):
    if not valor or not valor.isdigit():
        return False
    if len(valor) == 10:
        return is_valid_cedula(valor)
    if len(valor) == 13:
        return is_valid_ruc(valor)
    return False
