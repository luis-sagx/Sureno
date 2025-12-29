"""
Order Service - Handles order business logic
"""
from datetime import datetime
from bson.objectid import ObjectId
from models.order import OrderModel
from config import db


class OrderService:
    SHIPPING_COST = 3.0

    @staticmethod
    def get_all_orders():
        """Get all orders"""
        try:
            orders = OrderModel.get_all()
            return True, orders, 200
        except Exception as e:
            return False, str(e), 500

    @staticmethod
    def create_order(user_id, order_data):
        """
        Create a new order
        Returns: (success, result_data or error_message, status_code)
        """
        try:
            required_fields = ['address_id', 'cart_id']
            for field in required_fields:
                if field not in order_data:
                    return False, f"Falta el campo: {field}", 400

            # Validate cart exists
            cart = db.carritos.find_one({"_id": ObjectId(order_data['cart_id'])})
            if not cart:
                return False, "Carrito no encontrado", 404

            # Calculate total with shipping
            total_final = cart['total'] + OrderService.SHIPPING_COST

            # Prepare order document
            order_document = {
                "user_id": ObjectId(user_id),
                "address_id": ObjectId(order_data['address_id']),
                "cart_id": ObjectId(order_data['cart_id']),
                "total": total_final,
                "estado": "pendiente",
                "fecha": datetime.now()
            }

            order_id = OrderModel.create(order_document)
            return True, {
                "message": "Pedido creado exitosamente",
                "order_id": order_id
            }, 201

        except Exception as e:
            return False, str(e), 500

    @staticmethod
    def update_order_status(order_id, new_status):
        """
        Update order status
        Returns: (success, message or error_message, status_code)
        """
        try:
            if OrderModel.update_status(order_id, new_status):
                return True, "Estado del pedido actualizado", 200
            return False, "Pedido no encontrado o sin cambios", 404
        except Exception as e:
            return False, str(e), 500

    @staticmethod
    def cancel_order(order_id, user_id):
        """
        Cancel an order (user can only cancel their own orders)
        Returns: (success, message or error_message, status_code)
        """
        try:
            if not ObjectId.is_valid(order_id):
                return False, "ID inválido", 400

            result = db.orders.update_one(
                {"_id": ObjectId(order_id), "user_id": ObjectId(user_id)},
                {"$set": {"estado": "cancelado"}}
            )

            if result.modified_count > 0:
                return True, "Pedido cancelado exitosamente", 200
            return False, "Pedido no encontrado o no autorizado", 404

        except Exception as e:
            return False, str(e), 500

    @staticmethod
    def delete_order(order_id, user_id):
        """
        Delete an order (user can only delete their own orders)
        Returns: (success, message or error_message, status_code)
        """
        try:
            if not ObjectId.is_valid(order_id):
                return False, "ID inválido", 400

            result = db.orders.delete_one({
                "_id": ObjectId(order_id),
                "user_id": ObjectId(user_id)
            })

            if result.deleted_count == 0:
                return False, "Pedido no encontrado o no autorizado", 404

            return True, "Pedido eliminado exitosamente", 200

        except Exception as e:
            return False, str(e), 500

    @staticmethod
    def get_user_orders(user_id):
        """
        Get all orders for a specific user with full details
        Returns: (success, orders_data or error_message, status_code)
        """
        try:
            pipeline = [
                {"$match": {"user_id": ObjectId(user_id)}},
                {
                    "$lookup": {
                        "from": "carritos",
                        "localField": "cart_id",
                        "foreignField": "_id",
                        "as": "carrito_info"
                    }
                },
                {"$unwind": "$carrito_info"},
                {
                    "$lookup": {
                        "from": "addresses",
                        "localField": "address_id",
                        "foreignField": "_id",
                        "as": "direccion_info"
                    }
                },
                {"$unwind": "$direccion_info"},
                {"$sort": {"fecha": -1}},
                {
                    "$project": {
                        "_id": 0,
                        "fecha_formateada": {
                            "$dateToString": {
                                "format": "%d/%m/%Y %H:%M",
                                "date": "$fecha"
                            }
                        },
                        "total": 1,
                        "estado": 1,
                        "productos": "$carrito_info.productos",
                        "direccion": {
                            "provincia": "$direccion_info.provincia",
                            "canton": "$direccion_info.canton",
                            "parroquia": "$direccion_info.parroquia"
                        }
                    }
                }
            ]

            pedidos = list(db.orders.aggregate(pipeline))
            
            # Format prices
            for pedido in pedidos:
                pedido['total'] = f"${pedido['total']:.2f}"

            return True, pedidos, 200

        except Exception as e:
            return False, str(e), 500
