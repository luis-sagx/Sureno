from config import db
from bson.objectid import ObjectId

class CartModel:
    @staticmethod
    def create(cart_data):
        """ Crea un nuevo carrito en la base de datos """
        result = db.carritos.insert_one(cart_data)
        return str(result.inserted_id)

    @staticmethod
    def get_by_id(cart_id):
        """ Obtiene un carrito por su ID """
        cart = db.carritos.find_one({'_id': ObjectId(cart_id)})
        return cart

    @staticmethod
    def get_all():
        """ Obtiene todos los carritos """
        carts = list(db.carritos.find())
        return carts

    @staticmethod
    def update(cart_id, update_data):
        """ Actualiza un carrito existente """
        result = db.carritos.update_one({'_id': ObjectId(cart_id)}, {'$set': update_data})
        return result.modified_count

    @staticmethod
    def delete(cart_id):
        """ Elimina un carrito de la base de datos """
        result = db.carritos.delete_one({'_id': ObjectId(cart_id)})
        return result.deleted_count
