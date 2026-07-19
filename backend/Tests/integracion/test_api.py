"""Pruebas de integración de la API JSON /api (F2 de la migración a Astro).

Cubre los endpoints consumidos por el frontend Astro: auth, catálogo,
categorías, compras, stats de admin y carrito.
"""
from bson.objectid import ObjectId


# ---------------------- Auth JSON ----------------------

def test_api_login_exitoso(client, usuario_cliente):
    r = client.post("/api/login", json={"email": usuario_cliente["email"], "password": "Password123"})
    assert r.status_code == 200
    assert r.get_json()["redirect"] == "/"


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
    prod_id = db.productos.insert_one({"nombre": "Ron", "precio": 10}).inserted_id
    with client.session_transaction() as s:
        s["user_id"] = usuario_cliente["_id"]
    r = client.post("/api/cart", json={
        "productos": [{"id": str(prod_id), "cantidad": 2}], "total": 15.5,
    })
    assert r.status_code == 201
    assert db.carrito.count_documents({}) == 1


# ---------------------- Carrito: CP-24 (precio/total server-side) ----------------------

def test_api_cart_ignora_precio_y_total_manipulados(client, usuario_cliente, db):
    """El precio/total que envia el cliente no debe usarse: el servidor
    recalcula desde el precio real del producto en Mongo."""
    prod_id = db.productos.insert_one({"nombre": "Ron", "precio": 10}).inserted_id
    with client.session_transaction() as s:
        s["user_id"] = usuario_cliente["_id"]
    r = client.post("/api/cart", json={
        "productos": [{"id": str(prod_id), "cantidad": 3, "precio": 0}],
        "total": 0,
    })
    assert r.status_code == 201
    body = r.get_json()
    assert body["total"] == 30  # 10 (precio real) * 3, no 0

    cart = db.carrito.find_one({"_id": ObjectId(body["id"])})
    assert cart["total"] == 30
    assert cart["productos"][0]["precio"] == 10


def test_api_cart_cantidad_invalida_400(client, usuario_cliente, db):
    prod_id = db.productos.insert_one({"nombre": "Ron", "precio": 10}).inserted_id
    with client.session_transaction() as s:
        s["user_id"] = usuario_cliente["_id"]
    r = client.post("/api/cart", json={"productos": [{"id": str(prod_id), "cantidad": 0}]})
    assert r.status_code == 400


def test_api_cart_producto_no_encontrado_404(client, usuario_cliente):
    with client.session_transaction() as s:
        s["user_id"] = usuario_cliente["_id"]
    r = client.post("/api/cart", json={"productos": [{"id": str(ObjectId()), "cantidad": 1}]})
    assert r.status_code == 404


def test_api_cart_id_producto_invalido_404(client, usuario_cliente):
    with client.session_transaction() as s:
        s["user_id"] = usuario_cliente["_id"]
    r = client.post("/api/cart", json={"productos": [{"id": "no-es-un-objectid", "cantidad": 1}]})
    assert r.status_code == 404


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


# ---------------------- Admin: eliminar pedido ----------------------

def test_api_admin_delete_order_no_admin_401(client):
    from bson.objectid import ObjectId as OID
    assert client.delete(f"/api/admin/orders/{OID()}").status_code == 401


def test_api_admin_delete_order_admin(client, usuario_admin, db):
    from bson.objectid import ObjectId as OID
    oid = db.orders.insert_one({"user_id": OID(), "estado": "pendiente"}).inserted_id
    with client.session_transaction() as s:
        s["user_id"] = usuario_admin["_id"]
        s["rol"] = "administrador"
    r = client.delete(f"/api/admin/orders/{oid}")
    assert r.status_code == 200
    assert db.orders.count_documents({}) == 0


# ---------------------- Autorización de endpoints (hardening) ----------------------

def test_api_users_requiere_admin(client, usuario_cliente):
    # anónimo -> 401
    assert client.get("/api/users").status_code == 401
    # cliente autenticado pero sin rol admin -> 403
    with client.session_transaction() as s:
        s["user_id"] = usuario_cliente["_id"]
        s["rol"] = "cliente"
    assert client.get("/api/users").status_code == 403


def test_api_users_admin_sin_password(client, usuario_admin, db):
    with client.session_transaction() as s:
        s["user_id"] = usuario_admin["_id"]
        s["rol"] = "administrador"
    r = client.get("/api/users")
    assert r.status_code == 200
    assert all("password" not in u for u in r.get_json())


def test_api_orders_lista_requiere_admin(client, usuario_cliente):
    assert client.get("/api/orders").status_code == 401
    with client.session_transaction() as s:
        s["user_id"] = usuario_cliente["_id"]
        s["rol"] = "cliente"
    assert client.get("/api/orders").status_code == 403


def test_api_order_status_requiere_admin_y_valida_estado(client, usuario_admin, db):
    from bson.objectid import ObjectId as OID
    oid = db.orders.insert_one({"user_id": OID(), "estado": "pendiente"}).inserted_id
    # anónimo -> 401
    assert client.put(f"/api/orders/{oid}", json={"estado": "enviado"}).status_code == 401
    with client.session_transaction() as s:
        s["user_id"] = usuario_admin["_id"]
        s["rol"] = "administrador"
    # estado inválido -> 400
    assert client.put(f"/api/orders/{oid}", json={"estado": "hackeado"}).status_code == 400
    # estado válido -> 200
    assert client.put(f"/api/orders/{oid}", json={"estado": "enviado"}).status_code == 200


def test_api_products_mutacion_requiere_admin(client, usuario_cliente):
    assert client.post("/api/products", data={"nombre": "X"}).status_code == 401
    with client.session_transaction() as s:
        s["user_id"] = usuario_cliente["_id"]
        s["rol"] = "cliente"
    assert client.delete("/api/products/000000000000000000000000").status_code == 403


def test_api_addresses_lista_requiere_admin(client, usuario_cliente):
    assert client.get("/api/addresses").status_code == 401
    with client.session_transaction() as s:
        s["user_id"] = usuario_cliente["_id"]
        s["rol"] = "cliente"
    assert client.get("/api/addresses").status_code == 403


def test_api_address_detalle_bloquea_idor(client, usuario_cliente, db):
    from bson.objectid import ObjectId as OID
    otro = OID()  # dueño distinto
    aid = db.addresses.insert_one({"user_id": otro, "provincia": "P"}).inserted_id
    with client.session_transaction() as s:
        s["user_id"] = usuario_cliente["_id"]
        s["rol"] = "cliente"
    # dirección de otro usuario -> 403
    assert client.get(f"/api/addresses/{aid}").status_code == 403
