from config import db
from bson.objectid import ObjectId

class ProductModel:
    @staticmethod
    def create(product_data):
        if "categoria_id" in product_data:
            product_data["categoria_id"] = ObjectId(product_data["categoria_id"])

        if "imagen" not in product_data or not product_data["imagen"]:
            product_data["imagen"] = "/static/img/default-product.png"
            
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
        # Convertir categoria_id a ObjectId si está presente
        if "categoria_id" in update_data:
            update_data["categoria_id"] = ObjectId(update_data["categoria_id"])
            
        result = db.productos.update_one(
            {'_id': ObjectId(product_id)}, 
            {'$set': update_data}
        )
        return result.modified_count
    
    @staticmethod
    def update_image(product_id, image_path):
        if not image_path:
            return 0
        result = db.productos.update_one(
            {'_id': ObjectId(product_id)}, 
            {'$set': {'imagen': image_path}}
        )
        return result.modified_count

    @staticmethod
    def delete(product_id):
        result = db.productos.delete_one({'_id': ObjectId(product_id)})
        return result.deleted_count
