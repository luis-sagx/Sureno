"""Pruebas unitarias de models/ con mongomock (TAR-02).

Cobertura de UserModel, ProductModel, OrderModel y AddressModel. CartModel se
eliminó como código muerto en DEF-014, por lo que no se prueba.
"""
import bcrypt
import pytest
from bson.objectid import ObjectId

from models.user import UserModel
from models.product import ProductModel
from models.order import OrderModel
from models.address import AddressModel


# ---------------------- UserModel ----------------------

def test_cp18_user_create_hashea_password(db):
    """CP-18: create() almacena la contraseña con hash bcrypt, no en texto plano."""
    user_id = UserModel.create({"email": "u@test.com", "password": "secreto123"})
    guardado = db.usuarios.find_one({"_id": ObjectId(user_id)})
    assert guardado["password"] != "secreto123"
    assert bcrypt.checkpw(b"secreto123", guardado["password"].encode("utf-8"))


def test_user_get_by_email(db):
    UserModel.create({"email": "buscar@test.com", "password": "x"})
    assert UserModel.get_by_email("buscar@test.com")["email"] == "buscar@test.com"
    assert UserModel.get_by_email("no@existe.com") is None


def test_user_get_by_id_y_get_all(db):
    uid = UserModel.create({"email": "a@test.com", "password": "x"})
    assert UserModel.get_by_id(uid)["email"] == "a@test.com"
    UserModel.create({"email": "b@test.com", "password": "x"})
    assert len(UserModel.get_all()) == 2


def test_user_update_rehashea_password(db):
    uid = UserModel.create({"email": "up@test.com", "password": "vieja"})
    assert UserModel.update(uid, {"password": "nueva456"}) == 1
    guardado = db.usuarios.find_one({"_id": ObjectId(uid)})
    assert bcrypt.checkpw(b"nueva456", guardado["password"].encode("utf-8"))


def test_user_delete(db):
    uid = UserModel.create({"email": "del@test.com", "password": "x"})
    assert UserModel.delete(uid) == 1
    assert UserModel.get_by_id(uid) is None


# ---------------------- ProductModel ----------------------

def test_product_create_asigna_imagen_por_defecto(db):
    cat_id = str(ObjectId())
    pid = ProductModel.create({"nombre": "Ron", "precio": 10, "categoria_id": cat_id})
    guardado = db.productos.find_one({"_id": ObjectId(pid)})
    assert guardado["imagen"] == "/static/img/default-product.png"


def test_product_get_by_id_incluye_tipo_categoria(db):
    cat_id = db.categorias.insert_one({"nombre": "Rones"}).inserted_id
    pid = ProductModel.create({"nombre": "Ron", "precio": 10, "categoria_id": str(cat_id)})
    producto = ProductModel.get_by_id(pid)
    assert producto["tipo"] == "Rones"
    assert isinstance(producto["_id"], str)


def test_product_update_y_delete(db):
    cat_id = str(ObjectId())
    pid = ProductModel.create({"nombre": "Ron", "precio": 10, "categoria_id": cat_id})
    assert ProductModel.update(pid, {"precio": 20}) == 1
    assert db.productos.find_one({"_id": ObjectId(pid)})["precio"] == 20
    assert ProductModel.delete(pid) == 1
    assert ProductModel.get_by_id(pid) is None


def test_product_update_image_vacia_no_modifica(db):
    cat_id = str(ObjectId())
    pid = ProductModel.create({"nombre": "Ron", "precio": 10, "categoria_id": cat_id})
    assert ProductModel.update_image(pid, "") == 0


# ---------------------- OrderModel ----------------------

def _order_data(user_id):
    return {
        "user_id": ObjectId(user_id),
        "address_id": ObjectId(),
        "cart_id": ObjectId(),
        "total": 25.0,
    }


def test_order_create_estado_pendiente_y_fecha(db):
    uid = str(ObjectId())
    oid = OrderModel.create(_order_data(uid))
    guardado = db.orders.find_one({"_id": ObjectId(oid)})
    assert guardado["estado"] == "pendiente"
    assert "fecha" in guardado


def test_order_get_all_enriquece_datos_cliente(db):
    uid = db.usuarios.insert_one({"nombre": "Leo", "apellido": "Diaz", "cedula": "999"}).inserted_id
    OrderModel.create(_order_data(str(uid)))
    orders = OrderModel.get_all()
    assert orders[0]["nombre_cliente"] == "Leo"
    assert isinstance(orders[0]["user_id"], str)


def test_order_update_status(db):
    oid = OrderModel.create(_order_data(str(ObjectId())))
    assert OrderModel.update_status(oid, "cancelado") is True
    assert db.orders.find_one({"_id": ObjectId(oid)})["estado"] == "cancelado"


def test_order_delete_respeta_propietario(db):
    uid = str(ObjectId())
    oid = OrderModel.create(_order_data(uid))
    # Otro usuario no puede borrarla
    assert OrderModel.delete(oid, str(ObjectId())) is False
    # El propietario sí
    assert OrderModel.delete(oid, uid) is True


# ---------------------- AddressModel ----------------------

def _address_data(user_id):
    return {
        "provincia": "Pichincha", "canton": "Quito", "parroquia": "Centro",
        "calle_principal": "A", "calle_secundaria": "B", "codigo_postal": "170101",
        "user_id": user_id,
    }


def test_address_create_y_get_by_id(db):
    uid = str(ObjectId())
    aid = AddressModel.create(_address_data(uid))
    direccion = AddressModel.get_by_id(aid)
    assert direccion["provincia"] == "Pichincha"
    assert direccion["user_id"] == ObjectId(uid)


def test_address_create_falta_campo_lanza_valueerror(db):
    incompleta = {"provincia": "Pichincha"}
    with pytest.raises(ValueError):
        AddressModel.create(incompleta)
