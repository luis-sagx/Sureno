"""
Cart Service - Handles cart business logic
"""
from datetime import datetime
from bson.objectid import ObjectId
from models.cart import CartModel
from config import db


class CartService:
    @staticmethod
    def get_all_carts():
        """Get all carts"""
        carts = CartModel.get_all()
        for cart in carts:
            cart['_id'] = str(cart['_id'])
        return carts

    @staticmethod
    def get_cart_by_id(cart_id):
        """
        Get cart by ID
        Returns: (success, cart_data or error_message, status_code)
        """
        try:
            cart = CartModel.get_by_id(cart_id)
            if cart:
                cart['_id'] = str(cart['_id'])
                cart['user_id'] = str(cart['user_id'])
                return True, cart, 200
            return False, "Carrito no encontrado", 404
        except Exception as e:
            return False, str(e), 500

    @staticmethod
    def create_cart(user_id, cart_data):
        """
        Create a new cart for user
        Returns: (success, result_data or error_message, status_code)
        """
        try:
            if not cart_data:
                return False, "Datos no recibidos", 400

            cart_document = {
                "user_id": ObjectId(user_id),
                "productos": cart_data['productos'],
                "total": cart_data['total'],
                "fecha_creacion": datetime.now()
            }

            result = db.carritos.insert_one(cart_document)
            return True, {
                'message': 'Carrito guardado',
                'id': str(result.inserted_id),
                'total': cart_data['total']
            }, 201
        except Exception as e:
            return False, str(e), 500

    @staticmethod
    def update_cart(cart_id, update_data):
        """
        Update cart
        Returns: (success, message or error_message, status_code)
        """
        try:
            modified_count = CartModel.update(cart_id, update_data)
            if modified_count:
                return True, "Carrito actualizado", 200
            return False, "Carrito no encontrado o sin cambios", 404
        except Exception as e:
            return False, str(e), 500

    @staticmethod
    def delete_cart(cart_id):
        """
        Delete cart
        Returns: (success, message or error_message, status_code)
        """
        try:
            deleted_count = CartModel.delete(cart_id)
            if deleted_count:
                return True, "Carrito eliminado", 200
            return False, "Carrito no encontrado", 404
        except Exception as e:
            return False, str(e), 500
