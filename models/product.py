from config import db
from bson.objectid import ObjectId

class ProductModel:
    @staticmethod
    def create(product_data):
        categoria = db.categorias.find_one({"_id": ObjectId(product_data["categoria_id"])})
        if not categoria:
            return None  # No crear si la categoría no existe

        result = db.productos.insert_one(product_data)
        return str(result.inserted_id)

    @staticmethod
    def get_by_id(product_id):
        producto = db.productos.find_one({"_id": ObjectId(product_id)})

        if producto:
            producto["_id"] = str(producto["_id"])  # Convertimos el ObjectId a string
            producto["categoria_id"] = str(producto["categoria_id"])  # Convertir ID a string

            # 🔹 Obtener la categoría desde la colección `categorias`
            categoria = db.categorias.find_one({"_id": ObjectId(producto["categoria_id"])})
            producto["tipo"] = categoria["nombre"] if categoria else "Desconocido"

            return producto
        return None

    @staticmethod
    def get_all():
        products = list(db.productos.find({}))  # Se usa {} para traer todos los productos
        return products


    @staticmethod
    def update(product_id, update_data):
        result = db.productos.update_one({'_id': ObjectId(product_id)}, {'$set': update_data})
        return result.modified_count

    @staticmethod
    def delete(product_id):
        result = db.productos.delete_one({'_id': ObjectId(product_id)})
        return result.deleted_count
