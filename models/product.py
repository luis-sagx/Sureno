from config import db
from bson.objectid import ObjectId

class ProductModel:
    @staticmethod
    def create(product_data):
        result = db.productos.insert_one(product_data)
        return str(result.inserted_id)

    @staticmethod
    def get_by_id(product_id):
        product = db.productos.find_one({'_id': ObjectId(product_id)})
        return product

    @staticmethod
    def get_all():
        products = list(db.productos.find())
        return products

    @staticmethod
    def update(product_id, update_data):
        result = db.productos.update_one({'_id': ObjectId(product_id)}, {'$set': update_data})
        return result.modified_count

    @staticmethod
    def delete(product_id):
        result = db.productos.delete_one({'_id': ObjectId(product_id)})
        return result.deleted_count
