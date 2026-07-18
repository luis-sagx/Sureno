"""Pruebas de integración de la API JSON /api (F2 de la migración a Astro).

Cubre los endpoints consumidos por el frontend Astro: auth, catálogo,
categorías, compras, stats de admin y carrito.
"""
from bson.objectid import ObjectId


# ---------------------- Auth JSON ----------------------

def test_api_login_exitoso(client, usuario_cliente):
    r = client.post("/api/login", json={"email": usuario_cliente["email"], "password": "Password123"})
    assert r.status_code == 200
    assert r.get_json()["redirect"] == "/index"


def test_api_login_password_incorrecta(client, usuario_cliente):
    r = client.post("/api/login", json={"email": usuario_cliente["email"], "password": "mala"})
    assert r.status_code == 401


def test_api_signup_crea_usuario(client, db):
    db.roles.insert_one({"id_rol": 1, "rol": "cliente"})
    r = client.post("/api/signup", json={
        "email": "n@test.com", "nombre": "N", "apellido": "U",
        "password": "Clave123", "cedula": "1234567890",
    })
    assert r.status_code == 201
    assert db.usuarios.find_one({"email": "n@test.com"}) is not None


def test_api_signup_email_duplicado(client, db, usuario_cliente):
    db.roles.insert_one({"id_rol": 1, "rol": "cliente"})
    r = client.post("/api/signup", json={
        "email": usuario_cliente["email"], "nombre": "N", "apellido": "U",
        "password": "Clave123", "cedula": "1",
    })
    assert r.status_code == 409


def test_api_logout_limpia_sesion(client, usuario_cliente):
    with client.session_transaction() as s:
        s["user_id"] = usuario_cliente["_id"]
    assert client.post("/api/logout").status_code == 200
    # Tras logout, /api/user responde 401
    assert client.get("/api/user").status_code == 401


# ---------------------- Catálogo / categorías ----------------------

def test_api_products_lista_json(client, db):
    db.productos.insert_one({"nombre": "Ron", "precio": 10, "categoria_id": ObjectId()})
    r = client.get("/api/products")
    assert r.status_code == 200
    body = r.get_json()
    assert isinstance(body, list) and body[0]["nombre"] == "Ron"
    assert isinstance(body[0]["_id"], str)


def test_api_product_detail_404(client):
    assert client.get(f"/api/products/{ObjectId()}").status_code == 404


def test_api_categories_lista_json(client, db):
    db.categorias.insert_one({"nombre": "Rones"})
    r = client.get("/api/categories")
    assert r.status_code == 200
    assert r.get_json()[0]["nombre"] == "Rones"


# ---------------------- Compras ----------------------

def test_api_compras_sin_sesion_401(client):
    assert client.get("/api/compras").status_code == 401


def test_api_compras_autenticado_lista(client, usuario_cliente):
    with client.session_transaction() as s:
        s["user_id"] = usuario_cliente["_id"]
    r = client.get("/api/compras")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)


# ---------------------- Admin stats ----------------------

def test_api_admin_stats_sin_sesion_401(client):
    assert client.get("/api/admin/stats").status_code == 401


def test_api_admin_stats_cliente_403(client, usuario_cliente):
    with client.session_transaction() as s:
        s["user_id"] = usuario_cliente["_id"]
        s["rol"] = "cliente"
    assert client.get("/api/admin/stats").status_code == 403


def test_api_admin_stats_admin_200(client, usuario_admin, db):
    db.productos.insert_one({"nombre": "X"})
    with client.session_transaction() as s:
        s["user_id"] = usuario_admin["_id"]
        s["rol"] = "administrador"
    r = client.get("/api/admin/stats")
    assert r.status_code == 200
    assert r.get_json()["total_productos"] == 1


# ---------------------- Carrito ----------------------

def test_api_cart_sin_sesion_401(client):
    assert client.post("/api/cart", json={"productos": [], "total": 0}).status_code == 401


def test_api_cart_guarda(client, usuario_cliente, db):
    with client.session_transaction() as s:
        s["user_id"] = usuario_cliente["_id"]
    r = client.post("/api/cart", json={"productos": [{"id": "1"}], "total": 15.5})
    assert r.status_code == 201
    assert db.carrito.count_documents({}) == 1


# ---------------------- Direcciones ----------------------

def test_api_address_sin_sesion_401(client):
    assert client.post("/api/addresses", json={}).status_code == 401


def test_api_address_crea(client, usuario_cliente, db):
    with client.session_transaction() as s:
        s["user_id"] = usuario_cliente["_id"]
    r = client.post("/api/addresses", json={
        "provincia": "P", "canton": "C", "parroquia": "Pa",
        "calle_principal": "A", "calle_secundaria": "B", "codigo_postal": "170101",
    })
    assert r.status_code == 201
    assert db.addresses.count_documents({}) == 1


# ---------------------- CSRF / sesión ----------------------

def test_api_csrf_devuelve_token(client):
    r = client.get("/api/csrf")
    assert r.status_code == 200
    assert r.get_json().get("csrfToken")


def test_api_user_incluye_rol(client, usuario_cliente):
    with client.session_transaction() as s:
        s["user_id"] = usuario_cliente["_id"]
        s["rol"] = "cliente"
    r = client.get("/api/user")
    assert r.status_code == 200
    assert r.get_json()["rol"] == "cliente"
