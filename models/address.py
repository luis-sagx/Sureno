from bson import ObjectId
from config import db

class AddressModel:
    @staticmethod
    def create(data):
        # Validar campos requeridos
        required_fields = ['provincia', 'canton', 'parroquia', 'calle_principal', 'calle_secundaria', 'codigo_postal', 'user_id']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Campo requerido faltante: {field}")

        # Insertar en la base de datos
        result = db.addresses.insert_one({
            **data,
            "user_id": ObjectId(data['user_id'])
        })
        
        return str(result.inserted_id)  # Devolver ID como string
    
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
