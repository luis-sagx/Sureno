from config import db
from bson.objectid import ObjectId

class AddressModel:
    @staticmethod
    def create(direccion_data):
        result = db.direcciones.insert_one(direccion_data)
        return str(result.inserted_id)

    @staticmethod
    def get_by_id(direccion_id):
        direccion = db.direcciones.find_one({'_id': ObjectId(direccion_id)})
        return direccion

    @staticmethod
    def get_all():
        direcciones = list(db.direcciones.find())
        return direcciones

    @staticmethod
    def update(direccion_id, update_data):
        result = db.direcciones.update_one({'_id': ObjectId(direccion_id)}, {'$set': update_data})
        return result.modified_count

    @staticmethod
    def delete(direccion_id):
        result = db.direcciones.delete_one({'_id': ObjectId(direccion_id)})
        return result.deleted_count
