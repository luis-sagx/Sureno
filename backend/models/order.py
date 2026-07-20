from datetime import datetime
from bson import ObjectId
from config import db

class OrderModel:
    @staticmethod
    def _serialize_with_customer(order):
        """Normaliza ObjectId y agrega los datos visibles del cliente."""
        for field in ("_id", "user_id", "address_id", "cart_id"):
            order[field] = str(order[field])

        user = db.usuarios.find_one({"_id": ObjectId(order["user_id"])}) or {}
        for field in ("nombre", "apellido", "cedula"):
            order[f"{field}_cliente"] = user.get(field, "N/A")
        return order

    @staticmethod
    def create(order_data):
        order_data["fecha"] = datetime.now()
        order_data["estado"] = "pendiente"
        result = db.orders.insert_one(order_data)
        return str(result.inserted_id)

    @staticmethod
    def get_all():
        orders = list(db.orders.find())
        return [OrderModel._serialize_with_customer(order) for order in orders]

    @staticmethod
    def get_by_id(order_id):
        order = db.orders.find_one({"_id": ObjectId(order_id)})
        return OrderModel._serialize_with_customer(order) if order else None

    @staticmethod
    def update_status(order_id, new_status):
        result = db.orders.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"estado": new_status}}
        )
        return result.modified_count > 0

    @staticmethod
    def delete(order_id, user_id):
        result = db.orders.delete_one({
            "_id": ObjectId(order_id),
            "user_id": ObjectId(user_id)
        })
        return result.deleted_count > 0
