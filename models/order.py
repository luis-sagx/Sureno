from datetime import datetime
from bson import ObjectId
from config import db

class OrderModel:
    @staticmethod
    def create(order_data):
        order_data["fecha"] = datetime.now()
        order_data["estado"] = "pendiente"
        result = db.orders.insert_one(order_data)
        return str(result.inserted_id)

    @staticmethod
    def get_all():
        orders = list(db.orders.find())
        for order in orders:
            order["_id"] = str(order["_id"])
            order["user_id"] = str(order["user_id"])
            order["address_id"] = str(order["address_id"])
            order["cart_id"] = str(order["cart_id"])

            # Obtener datos del usuario
            user = db.usuarios.find_one({"_id": ObjectId(order["user_id"])})
            if user:
                order["nombre_cliente"] = user.get("nombre", "N/A")
                order["apellido_cliente"] = user.get("apellido", "N/A")
                order["cedula_cliente"] = user.get("cedula", "N/A")
            else:
                order["nombre_cliente"] = "N/A"
                order["apellido_cliente"] = "N/A"
                order["cedula_cliente"] = "N/A"

        return orders

    @staticmethod
    def get_by_id(order_id):
        order = db.orders.find_one({"_id": ObjectId(order_id)})
        if order:
            order["_id"] = str(order["_id"])
            order["user_id"] = str(order["user_id"])
            order["address_id"] = str(order["address_id"])
            order["cart_id"] = str(order["cart_id"])

            # Obtener datos del usuario
            user = db.usuarios.find_one({"_id": ObjectId(order["user_id"])})
            if user:
                order["nombre_cliente"] = user.get("nombre", "N/A")
                order["apellido_cliente"] = user.get("apellido", "N/A")
                order["cedula_cliente"] = user.get("cedula", "N/A")
            else:
                order["nombre_cliente"] = "N/A"
                order["apellido_cliente"] = "N/A"
                order["cedula_cliente"] = "N/A"

        return order

    @staticmethod
    def update_status(order_id, new_status):
        result = db.orders.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"estado": new_status}}
        )
        return result.modified_count > 0

    @staticmethod
    def delete(order_id):
        result = db.orders.delete_one({"_id": ObjectId(order_id)})
        return result.deleted_count > 0