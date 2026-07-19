"""Pruebas unitarias adicionales de models/ (TAR-06).

Cubre ramas de error, casos límite y métodos no ejercitados por
test_models.py: OrderModel.get_by_id, AddressModel (excepciones y CRUD
restante) y CategoryModel.
"""
from bson.objectid import ObjectId

from models.order import OrderModel
from models.address import AddressModel
from models.category import CategoryModel
from models.product import ProductModel


# ---------------------- OrderModel ----------------------

def _order_data(user_id):
    return {
        "user_id": ObjectId(user_id),
        "address_id": ObjectId(),
        "cart_id": ObjectId(),
        "total": 25.0,
    }


def test_order_get_all_usuario_no_encontrado(db):
    """Si el usuario del pedido no existe, se rellenan campos N/A."""
    oid_usuario = ObjectId()  # no existe en usuarios
    OrderModel.create(_order_data(str(oid_usuario)))
    orders = OrderModel.get_all()
    assert orders[0]["nombre_cliente"] == "N/A"
    assert orders[0]["apellido_cliente"] == "N/A"
    assert orders[0]["cedula_cliente"] == "N/A"


def test_order_get_by_id_enriquece_datos_cliente(db):
    uid = db.usuarios.insert_one({"nombre": "Leo", "apellido": "Diaz", "cedula": "999"}).inserted_id
    oid = OrderModel.create(_order_data(str(uid)))
    order = OrderModel.get_by_id(oid)
    assert order["nombre_cliente"] == "Leo"
    assert order["apellido_cliente"] == "Diaz"
    assert order["cedula_cliente"] == "999"
    assert isinstance(order["_id"], str)
    assert isinstance(order["user_id"], str)


def test_order_get_by_id_usuario_no_encontrado(db):
    oid_usuario = ObjectId()
    oid = OrderModel.create(_order_data(str(oid_usuario)))
    order = OrderModel.get_by_id(oid)
    assert order["nombre_cliente"] == "N/A"
    assert order["apellido_cliente"] == "N/A"
    assert order["cedula_cliente"] == "N/A"


def test_order_get_by_id_inexistente(db):
    assert OrderModel.get_by_id(str(ObjectId())) is None


# ---------------------- AddressModel ----------------------

def test_address_get_by_id_objectid_directo(db):
    """Acepta un ObjectId ya construido (no solo str)."""
    aid = db.addresses.insert_one({"provincia": "P"}).inserted_id
    direccion = AddressModel.get_by_id(aid)
    assert direccion["provincia"] == "P"


def test_address_get_by_id_id_invalido_retorna_none(db):
    """Un id inválido no lanza excepción, retorna None (rama except)."""
    assert AddressModel.get_by_id("no-es-un-objectid") is None


def test_address_get_all(db):
    db.direcciones.insert_one({"provincia": "P"})
    direcciones = AddressModel.get_all()
    assert len(direcciones) == 1


def test_address_update(db):
    aid = db.direcciones.insert_one({"provincia": "P"}).inserted_id
    assert AddressModel.update(str(aid), {"provincia": "Q"}) == 1
    assert db.direcciones.find_one({"_id": aid})["provincia"] == "Q"


def test_address_delete(db):
    aid = db.direcciones.insert_one({"provincia": "P"}).inserted_id
    assert AddressModel.delete(str(aid)) == 1
    assert db.direcciones.find_one({"_id": aid}) is None


# ---------------------- CategoryModel ----------------------

def test_category_get_all(db):
    db.categorias.insert_one({"nombre": "Rones"})
    categorias = CategoryModel.get_all()
    assert len(categorias) == 1
    assert categorias[0]["nombre"] == "Rones"


def test_category_get_by_id(db):
    cid = db.categorias.insert_one({"nombre": "Whiskys"}).inserted_id
    categoria = CategoryModel.get_by_id(str(cid))
    assert categoria["nombre"] == "Whiskys"


def test_category_create(db):
    cid = CategoryModel.create({"nombre": "Vinos"})
    assert db.categorias.find_one({"_id": ObjectId(cid)})["nombre"] == "Vinos"


# ---------------------- ProductModel (ramas restantes) ----------------------

def test_product_update_con_categoria_id_la_convierte_a_objectid(db):
    cat_id = str(ObjectId())
    pid = ProductModel.create({"nombre": "Ron", "precio": 10, "categoria_id": cat_id})
    nueva_cat = str(ObjectId())
    assert ProductModel.update(pid, {"categoria_id": nueva_cat}) == 1
    guardado = db.productos.find_one({"_id": ObjectId(pid)})
    assert guardado["categoria_id"] == ObjectId(nueva_cat)


def test_product_update_image_con_ruta_actualiza(db):
    cat_id = str(ObjectId())
    pid = ProductModel.create({"nombre": "Ron", "precio": 10, "categoria_id": cat_id})
    assert ProductModel.update_image(pid, "/static/uploads/nueva.png") == 1
    guardado = db.productos.find_one({"_id": ObjectId(pid)})
    assert guardado["imagen"] == "/static/uploads/nueva.png"
