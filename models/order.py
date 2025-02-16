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