"""Pruebas de integración adicionales (TAR-06) para elevar cobertura de
routes/ y app.py: ramas de error, validaciones, 404s y flujos admin/cliente
completos que test_api.py no ejercitaba todavía.
"""
import io

import pytest
from bson.objectid import ObjectId


@pytest.fixture(autouse=True)
def _upload_folder_temporal(tmp_path, monkeypatch):
    """Evita que las pruebas de subida de imagen escriban en static/uploads
    real del repo: redirige UPLOAD_FOLDER a un directorio temporal."""
    import sys
    import importlib
    product_routes_module = sys.modules.get("routes.product_routes") or importlib.import_module("routes.product_routes")
    monkeypatch.setattr(product_routes_module, "UPLOAD_FOLDER", str(tmp_path))


def _login_admin(client, usuario_admin):
    with client.session_transaction() as s:
        s["user_id"] = usuario_admin["_id"]
        s["rol"] = "administrador"


def _login_cliente(client, usuario_cliente):
    with client.session_transaction() as s:
        s["user_id"] = usuario_cliente["_id"]
        s["rol"] = "cliente"


# ============================================================
# app.py
# ============================================================

def test_api_user_usuario_no_encontrado(client, db):
    """api_user: sesión con user_id que ya no existe en la BD -> 404."""
    with client.session_transaction() as s:
        s["user_id"] = str(ObjectId())
    r = client.get("/api/user")
    assert r.status_code == 404


def test_api_login_faltan_datos(client):
    r = client.post("/api/login", json={"email": "solo@correo.com"})
    assert r.status_code == 400


def test_api_login_usuario_no_encontrado(client, db):
    r = client.post("/api/login", json={"email": "no-existe@test.com", "password": "x"})
    assert r.status_code == 404


def test_api_login_rol_no_encontrado(client, db):
    import bcrypt
    hashed = bcrypt.hashpw(b"Password123", bcrypt.gensalt()).decode("utf-8")
    db.usuarios.insert_one({"email": "sinrol@test.com", "password": hashed, "id_rol": 999})
    r = client.post("/api/login", json={"email": "sinrol@test.com", "password": "Password123"})
    assert r.status_code == 500


def test_api_login_rol_no_reconocido(client, db):
    import bcrypt
    hashed = bcrypt.hashpw(b"Password123", bcrypt.gensalt()).decode("utf-8")
    db.roles.insert_one({"id_rol": 3, "rol": "otro"})
    db.usuarios.insert_one({"email": "raro@test.com", "password": hashed, "id_rol": 3})
    r = client.post("/api/login", json={"email": "raro@test.com", "password": "Password123"})
    assert r.status_code == 403


def test_api_login_excepcion_500(client):
    """Body no-JSON con Content-Type json fuerza una excepción en get_json()."""
    r = client.post("/api/login", data="{no es json", content_type="application/json")
    assert r.status_code == 500


def test_api_signup_faltan_campos(client, db):
    r = client.post("/api/signup", json={"email": "a@test.com"})
    assert r.status_code == 400


def test_api_signup_sin_rol_cliente_configurado(client, db):
    """No existe rol 'cliente' en BD -> 500 (error de configuración)."""
    r = client.post("/api/signup", json={
        "email": "x@test.com", "nombre": "X", "apellido": "Y",
        "password": "Clave123", "cedula": "1",
    })
    assert r.status_code == 500


def test_api_signup_excepcion_500(client, db):
    r = client.post("/api/signup", data="{no es json", content_type="application/json")
    assert r.status_code == 500


def test_api_get_cart_no_encontrado(client):
    assert client.get(f"/api/cart/{ObjectId()}").status_code == 404


def test_api_get_cart_encontrado(client, db):
    cid = db.carrito.insert_one({"total": 15.5, "productos": [{"id": "1"}]}).inserted_id
    r = client.get(f"/api/cart/{cid}")
    assert r.status_code == 200
    body = r.get_json()
    assert body["total"] == 15.5
    assert body["_id"] == str(cid)


def test_api_get_cart_id_invalido_500(client):
    r = client.get("/api/cart/no-es-un-id-valido")
    assert r.status_code == 500


def test_api_cart_datos_no_recibidos(client, usuario_cliente):
    _login_cliente(client, usuario_cliente)
    assert client.post("/api/cart", json={"total": 0}).status_code == 400


def test_api_compras_con_pedido_completo(client, usuario_cliente, db):
    """Ejercita el pipeline de agregación completo de _compras_de_usuario."""
    from datetime import datetime
    uid = ObjectId(usuario_cliente["_id"])
    cart_id = db.carrito.insert_one({"productos": [{"id": "1"}], "total": 10}).inserted_id
    address_id = db.addresses.insert_one({
        "provincia": "Pichincha", "canton": "Quito", "parroquia": "Centro",
    }).inserted_id
    db.orders.insert_one({
        "user_id": uid, "cart_id": cart_id, "address_id": address_id,
        "total": 13.0, "estado": "pendiente", "fecha": datetime.now(),
    })
    _login_cliente(client, usuario_cliente)
    r = client.get("/api/compras")
    assert r.status_code == 200
    pedidos = r.get_json()
    assert len(pedidos) == 1
    assert pedidos[0]["total"] == "$13.00"
    assert pedidos[0]["direccion"]["provincia"] == "Pichincha"


def test_api_compras_excepcion_500(client, usuario_cliente, monkeypatch):
    import app as app_module

    def _raise(user_id):
        raise RuntimeError("boom")

    monkeypatch.setattr(app_module, "_compras_de_usuario", _raise)
    _login_cliente(client, usuario_cliente)
    r = client.get("/api/compras")
    assert r.status_code == 500


def test_api_admin_delete_order_id_invalido(client, usuario_admin):
    _login_admin(client, usuario_admin)
    assert client.delete("/api/admin/orders/no-valido").status_code == 400


def test_api_admin_delete_order_no_encontrado(client, usuario_admin):
    _login_admin(client, usuario_admin)
    assert client.delete(f"/api/admin/orders/{ObjectId()}").status_code == 404


# ============================================================
# routes/address_routes.py
# ============================================================

def test_address_create_falta_campo_400(client, usuario_cliente):
    _login_cliente(client, usuario_cliente)
    r = client.post("/api/addresses", json={"provincia": "P"})
    assert r.status_code == 400


def test_address_create_excepcion_500(client, usuario_cliente, monkeypatch):
    from models.address import AddressModel
    _login_cliente(client, usuario_cliente)

    def _raise(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(AddressModel, "create", staticmethod(_raise))
    r = client.post("/api/addresses", json={
        "provincia": "P", "canton": "C", "parroquia": "Pa",
        "calle_principal": "A", "calle_secundaria": "B", "codigo_postal": "170101",
    })
    assert r.status_code == 500


def test_address_get_addresses_admin_200(client, usuario_admin, db):
    # Nota: AddressModel.get_all() lee de la colección "direcciones" (no
    # "addresses", donde create/get_by_id/update/delete sí operan) - se
    # respeta el comportamiento actual del modelo, solo se documenta aquí.
    # user_id como str: get_addresses solo serializa "_id" a str, no "user_id"
    # (comportamiento actual de la ruta, no se modifica aquí).
    db.direcciones.insert_one({"user_id": str(ObjectId()), "provincia": "P"})
    _login_admin(client, usuario_admin)
    r = client.get("/api/addresses")
    assert r.status_code == 200
    assert len(r.get_json()) == 1


def test_address_get_address_id_invalido_400(client, usuario_cliente):
    _login_cliente(client, usuario_cliente)
    assert client.get("/api/addresses/no-valido").status_code == 400


def test_address_get_address_no_encontrada_404(client, usuario_cliente):
    _login_cliente(client, usuario_cliente)
    assert client.get(f"/api/addresses/{ObjectId()}").status_code == 404


def test_address_get_address_propietario_200(client, usuario_cliente, db):
    aid = db.addresses.insert_one({
        "user_id": ObjectId(usuario_cliente["_id"]), "provincia": "P",
    }).inserted_id
    _login_cliente(client, usuario_cliente)
    r = client.get(f"/api/addresses/{aid}")
    assert r.status_code == 200
    assert r.get_json()["provincia"] == "P"


def test_address_get_address_admin_puede_ver_de_otro(client, usuario_admin, db):
    aid = db.addresses.insert_one({"user_id": ObjectId(), "provincia": "Q"}).inserted_id
    _login_admin(client, usuario_admin)
    assert client.get(f"/api/addresses/{aid}").status_code == 200


def test_address_update_id_invalido_400(client, usuario_cliente):
    _login_cliente(client, usuario_cliente)
    assert client.put("/api/addresses/no-valido", json={}).status_code == 400


def test_address_update_no_encontrada_404(client, usuario_cliente):
    _login_cliente(client, usuario_cliente)
    assert client.put(f"/api/addresses/{ObjectId()}", json={}).status_code == 404


def test_address_update_no_autorizado_403(client, usuario_cliente, db):
    aid = db.addresses.insert_one({"user_id": ObjectId(), "provincia": "P"}).inserted_id
    _login_cliente(client, usuario_cliente)
    assert client.put(f"/api/addresses/{aid}", json={"provincia": "Z"}).status_code == 403


def test_address_update_propietario_200(client, usuario_cliente, db):
    aid = db.addresses.insert_one({
        "user_id": ObjectId(usuario_cliente["_id"]), "provincia": "P",
    }).inserted_id
    _login_cliente(client, usuario_cliente)
    r = client.put(f"/api/addresses/{aid}", json={"provincia": "Z", "user_id": str(ObjectId())})
    assert r.status_code == 200
    guardado = db.addresses.find_one({"_id": aid})
    assert guardado["provincia"] == "Z"
    assert guardado["user_id"] == ObjectId(usuario_cliente["_id"])  # no se reasigna dueño


def test_address_update_sin_cambios_404(client, usuario_cliente, db):
    aid = db.addresses.insert_one({
        "user_id": ObjectId(usuario_cliente["_id"]), "provincia": "P",
    }).inserted_id
    _login_cliente(client, usuario_cliente)
    r = client.put(f"/api/addresses/{aid}", json={"provincia": "P"})
    assert r.status_code == 404


def test_address_delete_id_invalido_400(client, usuario_cliente):
    _login_cliente(client, usuario_cliente)
    assert client.delete("/api/addresses/no-valido").status_code == 400


def test_address_delete_propietario_200(client, usuario_cliente, db):
    aid = db.addresses.insert_one({
        "user_id": ObjectId(usuario_cliente["_id"]), "provincia": "P",
    }).inserted_id
    _login_cliente(client, usuario_cliente)
    assert client.delete(f"/api/addresses/{aid}").status_code == 200
    assert db.addresses.find_one({"_id": aid}) is None


def test_address_delete_no_autorizado_404(client, usuario_cliente, db):
    aid = db.addresses.insert_one({"user_id": ObjectId(), "provincia": "P"}).inserted_id
    _login_cliente(client, usuario_cliente)
    assert client.delete(f"/api/addresses/{aid}").status_code == 404


def test_address_delete_admin_puede_borrar_de_otro(client, usuario_admin, db):
    aid = db.addresses.insert_one({"user_id": ObjectId(), "provincia": "P"}).inserted_id
    _login_admin(client, usuario_admin)
    assert client.delete(f"/api/addresses/{aid}").status_code == 200


# ============================================================
# routes/order_routes.py
# ============================================================

def test_order_create_sin_sesion_401(client):
    assert client.post("/api/orders", json={}).status_code == 401


def test_order_create_datos_invalidos_400(client, usuario_cliente):
    _login_cliente(client, usuario_cliente)
    r = client.post("/api/orders", json={})
    assert r.status_code == 400


def test_order_create_falta_campo_400(client, usuario_cliente):
    _login_cliente(client, usuario_cliente)
    r = client.post("/api/orders", json={"address_id": str(ObjectId())})
    assert r.status_code == 400


def test_order_create_carrito_no_encontrado_404(client, usuario_cliente):
    _login_cliente(client, usuario_cliente)
    r = client.post("/api/orders", json={
        "address_id": str(ObjectId()), "cart_id": str(ObjectId()),
    })
    assert r.status_code == 404


def test_order_create_exitoso_201(client, usuario_cliente, db):
    cart_id = db.carrito.insert_one({"total": 20, "productos": []}).inserted_id
    _login_cliente(client, usuario_cliente)
    r = client.post("/api/orders", json={
        "address_id": str(ObjectId()), "cart_id": str(cart_id),
    })
    assert r.status_code == 201
    assert db.orders.count_documents({}) == 1


def test_order_create_excepcion_500(client, usuario_cliente):
    _login_cliente(client, usuario_cliente)
    r = client.post("/api/orders", json={
        "address_id": str(ObjectId()), "cart_id": "no-es-un-objectid",
    })
    assert r.status_code == 500


def test_order_get_all_orders_admin_200(client, usuario_admin, db):
    db.orders.insert_one({
        "user_id": ObjectId(), "address_id": ObjectId(), "cart_id": ObjectId(),
        "total": 1, "estado": "pendiente",
    })
    _login_admin(client, usuario_admin)
    r = client.get("/api/orders")
    assert r.status_code == 200
    assert len(r.get_json()) == 1


def test_order_get_all_orders_excepcion_500(client, usuario_admin, monkeypatch):
    from models.order import OrderModel

    def _raise():
        raise RuntimeError("boom")

    monkeypatch.setattr(OrderModel, "get_all", staticmethod(_raise))
    _login_admin(client, usuario_admin)
    r = client.get("/api/orders")
    assert r.status_code == 500


def test_order_update_status_excepcion_500(client, usuario_admin, db, monkeypatch):
    from models.order import OrderModel
    oid = db.orders.insert_one({"user_id": ObjectId(), "estado": "pendiente"}).inserted_id

    def _raise(order_id, new_status):
        raise RuntimeError("boom")

    monkeypatch.setattr(OrderModel, "update_status", staticmethod(_raise))
    _login_admin(client, usuario_admin)
    r = client.put(f"/api/orders/{oid}", json={"estado": "enviado"})
    assert r.status_code == 500


def test_order_delete_excepcion_500(client, usuario_cliente, db, monkeypatch):
    # `db` (fixture) es el mismo objeto mongomock que usa routes.order_routes
    # (conftest parchea config.db antes de importar la app), así que
    # monkeypatchear su colección afecta directamente a la ruta.
    def _raise(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(db.orders, "delete_one", _raise)
    _login_cliente(client, usuario_cliente)
    r = client.delete(f"/api/orders/{ObjectId()}")
    assert r.status_code == 500


def test_cancelar_pedido_excepcion_500(client, usuario_cliente, db, monkeypatch):
    def _raise(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(db.orders, "update_one", _raise)
    _login_cliente(client, usuario_cliente)
    r = client.put(f"/api/orders/{ObjectId()}/cancelar")
    assert r.status_code == 500


def test_order_update_status_estado_no_proporcionado_400(client, usuario_admin, db):
    oid = db.orders.insert_one({"user_id": ObjectId(), "estado": "pendiente"}).inserted_id
    _login_admin(client, usuario_admin)
    r = client.put(f"/api/orders/{oid}", json={})
    assert r.status_code == 400


def test_order_update_status_no_encontrado_404(client, usuario_admin):
    _login_admin(client, usuario_admin)
    r = client.put(f"/api/orders/{ObjectId()}", json={"estado": "enviado"})
    assert r.status_code == 404


def test_order_delete_sin_sesion_401(client):
    assert client.delete(f"/api/orders/{ObjectId()}").status_code == 401


def test_order_delete_id_invalido_400(client, usuario_cliente):
    _login_cliente(client, usuario_cliente)
    assert client.delete("/api/orders/no-valido").status_code == 400


def test_order_delete_no_encontrado_404(client, usuario_cliente):
    _login_cliente(client, usuario_cliente)
    assert client.delete(f"/api/orders/{ObjectId()}").status_code == 404


def test_order_delete_propietario_200(client, usuario_cliente, db):
    uid = ObjectId(usuario_cliente["_id"])
    oid = db.orders.insert_one({"user_id": uid, "estado": "pendiente"}).inserted_id
    _login_cliente(client, usuario_cliente)
    r = client.delete(f"/api/orders/{oid}")
    assert r.status_code == 200
    assert db.orders.count_documents({}) == 0


def test_cancelar_pedido_sin_sesion_401(client):
    assert client.put(f"/api/orders/{ObjectId()}/cancelar").status_code == 401


def test_cancelar_pedido_no_encontrado_404(client, usuario_cliente):
    _login_cliente(client, usuario_cliente)
    r = client.put(f"/api/orders/{ObjectId()}/cancelar")
    assert r.status_code == 404


def test_cancelar_pedido_propietario_200(client, usuario_cliente, db):
    uid = ObjectId(usuario_cliente["_id"])
    oid = db.orders.insert_one({"user_id": uid, "estado": "pendiente"}).inserted_id
    _login_cliente(client, usuario_cliente)
    r = client.put(f"/api/orders/{oid}/cancelar")
    assert r.status_code == 200
    assert db.orders.find_one({"_id": oid})["estado"] == "cancelado"


# ============================================================
# routes/product_routes.py
# ============================================================

def test_upload_image_sin_archivo_400(client, usuario_admin):
    _login_admin(client, usuario_admin)
    r = client.post(f"/api/upload-image/{ObjectId()}", data={})
    assert r.status_code == 400


def test_upload_image_formato_no_permitido_400(client, usuario_admin):
    _login_admin(client, usuario_admin)
    data = {"imagen": (io.BytesIO(b"contenido"), "archivo.txt")}
    r = client.post(f"/api/upload-image/{ObjectId()}", data=data, content_type="multipart/form-data")
    assert r.status_code == 400


def test_upload_image_producto_no_encontrado_404(client, usuario_admin):
    _login_admin(client, usuario_admin)
    data = {"imagen": (io.BytesIO(b"contenido"), "foto.png")}
    r = client.post(f"/api/upload-image/{ObjectId()}", data=data, content_type="multipart/form-data")
    assert r.status_code == 404


def test_upload_image_exitoso_200(client, usuario_admin, db):
    from models.product import ProductModel
    cat_id = str(ObjectId())
    pid = ProductModel.create({"nombre": "Ron", "precio": 10, "categoria_id": cat_id})
    _login_admin(client, usuario_admin)
    data = {"imagen": (io.BytesIO(b"contenido"), "foto.png")}
    r = client.post(f"/api/upload-image/{pid}", data=data, content_type="multipart/form-data")
    assert r.status_code == 200
    assert r.get_json()["ruta"].endswith("foto.png")


def test_product_detail_200(client, db):
    from models.product import ProductModel
    cat_id = db.categorias.insert_one({"nombre": "Rones"}).inserted_id
    pid = ProductModel.create({"nombre": "Ron", "precio": 10, "categoria_id": str(cat_id)})
    r = client.get(f"/api/products/{pid}")
    assert r.status_code == 200
    assert r.get_json()["nombre"] == "Ron"


def test_create_product_201(client, usuario_admin, db):
    cat_id = db.categorias.insert_one({"nombre": "Rones"}).inserted_id
    _login_admin(client, usuario_admin)
    r = client.post("/api/products", data={
        "nombre": "Ron Añejo", "precio": "15.5", "stock": "10",
        "mililitros": "750", "categoria_id": str(cat_id),
    })
    assert r.status_code == 201
    assert db.productos.count_documents({}) == 1


def test_create_product_con_imagen_201(client, usuario_admin, db):
    cat_id = db.categorias.insert_one({"nombre": "Rones"}).inserted_id
    _login_admin(client, usuario_admin)
    data = {
        "nombre": "Ron Añejo", "precio": "15.5", "stock": "10",
        "mililitros": "750", "categoria_id": str(cat_id),
        "imagen": (io.BytesIO(b"contenido"), "foto.png"),
    }
    r = client.post("/api/products", data=data, content_type="multipart/form-data")
    assert r.status_code == 201


def test_create_product_error_al_crear_400(client, usuario_admin, db, monkeypatch):
    from models.product import ProductModel
    cat_id = db.categorias.insert_one({"nombre": "Rones"}).inserted_id
    monkeypatch.setattr(ProductModel, "create", staticmethod(lambda data: None))
    _login_admin(client, usuario_admin)
    r = client.post("/api/products", data={
        "nombre": "Ron Añejo", "precio": "15.5", "stock": "10",
        "mililitros": "750", "categoria_id": str(cat_id),
    })
    assert r.status_code == 400


def test_update_product_200(client, usuario_admin, db):
    from models.product import ProductModel
    cat_id = str(ObjectId())
    pid = ProductModel.create({"nombre": "Ron", "precio": 10, "categoria_id": cat_id})
    _login_admin(client, usuario_admin)
    r = client.put(f"/api/products/{pid}", data={
        "nombre": "Ron Nuevo", "precio": "20", "stock": "5",
        "mililitros": "700", "categoria_id": cat_id,
    })
    assert r.status_code == 200


def test_update_product_con_imagen_200(client, usuario_admin, db):
    from models.product import ProductModel
    cat_id = str(ObjectId())
    pid = ProductModel.create({"nombre": "Ron", "precio": 10, "categoria_id": cat_id})
    _login_admin(client, usuario_admin)
    data = {
        "nombre": "Ron Nuevo", "precio": "20", "stock": "5",
        "mililitros": "700", "categoria_id": cat_id,
        "imagen": (io.BytesIO(b"contenido"), "nueva.png"),
    }
    r = client.put(f"/api/products/{pid}", data=data, content_type="multipart/form-data")
    assert r.status_code == 200


def test_update_product_no_encontrado_404(client, usuario_admin):
    _login_admin(client, usuario_admin)
    r = client.put(f"/api/products/{ObjectId()}", data={
        "nombre": "X", "precio": "1", "stock": "1", "mililitros": "1", "categoria_id": str(ObjectId()),
    })
    assert r.status_code == 404


def test_update_product_excepcion_500(client, usuario_admin):
    _login_admin(client, usuario_admin)
    r = client.put(f"/api/products/{ObjectId()}", data={"nombre": "X"})
    assert r.status_code == 500


def test_delete_product_200(client, usuario_admin, db):
    from models.product import ProductModel
    cat_id = str(ObjectId())
    pid = ProductModel.create({"nombre": "Ron", "precio": 10, "categoria_id": cat_id})
    _login_admin(client, usuario_admin)
    assert client.delete(f"/api/products/{pid}").status_code == 200


def test_delete_product_no_encontrado_404(client, usuario_admin):
    _login_admin(client, usuario_admin)
    assert client.delete(f"/api/products/{ObjectId()}").status_code == 404


# ============================================================
# routes/user_routes.py
# ============================================================

def test_get_user_200(client, usuario_admin):
    r = _login_admin(client, usuario_admin)
    r = client.get(f"/api/users/{usuario_admin['_id']}")
    assert r.status_code == 200
    assert "password" not in r.get_json()


def test_get_user_no_encontrado_404(client, usuario_admin):
    _login_admin(client, usuario_admin)
    assert client.get(f"/api/users/{ObjectId()}").status_code == 404


def test_create_user_201(client, usuario_admin, db):
    _login_admin(client, usuario_admin)
    r = client.post("/api/users", json={
        "email": "nuevo@test.com", "password": "Clave123", "id_rol": 1,
    })
    assert r.status_code == 201
    assert db.usuarios.find_one({"email": "nuevo@test.com"}) is not None


def test_update_user_200_no_permite_cambiar_rol_ni_password(client, usuario_admin, db):
    uid = usuario_admin["_id"]
    _login_admin(client, usuario_admin)
    r = client.put(f"/api/users/{uid}", json={
        "nombre": "Cambiado", "id_rol": 999, "password": "otra",
    })
    assert r.status_code == 200
    guardado = db.usuarios.find_one({"_id": ObjectId(uid)})
    assert guardado["nombre"] == "Cambiado"
    assert guardado["id_rol"] != 999


def test_update_user_no_encontrado_404(client, usuario_admin):
    _login_admin(client, usuario_admin)
    r = client.put(f"/api/users/{ObjectId()}", json={"nombre": "X"})
    assert r.status_code == 404


def test_delete_user_200(client, usuario_admin, usuario_cliente):
    _login_admin(client, usuario_admin)
    assert client.delete(f"/api/users/{usuario_cliente['_id']}").status_code == 200


def test_delete_user_no_encontrado_404(client, usuario_admin):
    _login_admin(client, usuario_admin)
    assert client.delete(f"/api/users/{ObjectId()}").status_code == 404
