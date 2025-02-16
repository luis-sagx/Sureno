from config import db
from bson.objectid import ObjectId

class CategoryModel:
    @staticmethod
    def get_all():
        """Obtener todas las categorías."""
        return list(db.categorias.find({}))

    @staticmethod
    def get_by_id(category_id):
        """Obtener una categoría por su ID."""
        return db.categorias.find_one({"_id": ObjectId(category_id)})

    @staticmethod
    def create(category_data):
        """Crear una nueva categoría."""
        result = db.categorias.insert_one(category_data)
        return str(result.inserted_id)