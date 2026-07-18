"""Pruebas de integración de rutas con Flask test client (TAR-03).

Trazabilidad requisito ↔ caso ↔ código en nombres/docstrings. CP-07 y CP-19
documentan las regresiones que cubren DEF-010 (admin sin acceso) y DEF-011
(compra sin sesión).
"""


# ---------------------- Login (CP-04/05/06) ----------------------

def test_cp04_login_exitoso_cliente(client, usuario_cliente):
    """CP-04 / RF-02: login válido de cliente responde 200 y redirect a /index."""
    r = client.post("/login", json={"email": usuario_cliente["email"], "password": "Password123"})
    assert r.status_code == 200
    assert r.get_json()["redirect"] == "/index"


def test_cp05_login_password_incorrecta(client, usuario_cliente):
    """CP-05 / RF-02: contraseña incorrecta responde 401."""
    r = client.post("/login", json={"email": usuario_cliente["email"], "password": "mala"})
    assert r.status_code == 401


def test_cp05b_login_usuario_inexistente(client, db):
    """CP-05: usuario inexistente responde 404."""
    r = client.post("/login", json={"email": "no@existe.com", "password": "x"})
    assert r.status_code == 404


def test_cp06_login_admin_redirige_a_panel(client, usuario_admin):
    """CP-06 / RF-02: login de administrador redirige a /admin/home."""
    r = client.post("/login", json={"email": usuario_admin["email"], "password": "Password123"})
    assert r.status_code == 200
    assert r.get_json()["redirect"] == "/admin/home"


# ---------------------- Control de acceso admin (CP-07, DEF-010) ----------------------

def test_cp07_admin_sin_sesion_redirige_login(client):
    """CP-07 / DEF-010: /admin/home sin sesión redirige (302) a login."""
    r = client.get("/admin/home")
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]


def test_cp07b_admin_con_rol_cliente_denegado(client, usuario_cliente):
    """CP-07 / DEF-010: cliente autenticado no accede al panel admin (302)."""
    with client.session_transaction() as s:
        s["user_id"] = usuario_cliente["_id"]
        s["rol"] = "cliente"
    r = client.get("/admin/home")
    assert r.status_code == 302


def test_cp07c_admin_con_rol_administrador_accede(client, usuario_admin):
    """CP-07 / DEF-010: administrador autenticado sí accede (200)."""
    with client.session_transaction() as s:
        s["user_id"] = usuario_admin["_id"]
        s["rol"] = "administrador"
    assert client.get("/admin/home").status_code == 200


# ---------------------- signUp (CP-02) ----------------------

def test_cp02_signup_crea_usuario(client, db):
    """CP-02 / RF-01: registro válido crea el usuario y responde 200."""
    db.roles.insert_one({"id_rol": 1, "rol": "cliente"})
    r = client.post("/signUp", data={
        "email": "nuevo@test.com", "nombre": "Neo", "apellido": "Uno",
        "password": "Clave123", "cedula": "1234567890",
    })
    assert r.status_code == 200
    assert db.usuarios.find_one({"email": "nuevo@test.com"}) is not None


# ---------------------- /api/user (CP-20) ----------------------

def test_cp20_api_user_sin_sesion_401(client):
    """CP-20: /api/user sin sesión responde 401."""
    assert client.get("/api/user").status_code == 401


def test_cp20b_api_user_autenticado_200(client, usuario_cliente):
    """CP-20: /api/user autenticado devuelve los datos del usuario."""
    with client.session_transaction() as s:
        s["user_id"] = usuario_cliente["_id"]
    r = client.get("/api/user")
    assert r.status_code == 200
    assert r.get_json()["email"] == usuario_cliente["email"]


# ---------------------- /compras (CP-19, DEF-011) ----------------------

def test_cp19_compras_sin_sesion_redirige_login(client):
    """CP-19 / DEF-011: /compras sin sesión redirige (302) a login."""
    r = client.get("/compras")
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]
