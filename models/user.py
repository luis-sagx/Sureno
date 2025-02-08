from config import db
from bson.objectid import ObjectId
import bcrypt

class UserModel:
    @staticmethod
    def create(user_data):
        # Hashear la contraseña antes de guardar
        hashed_password = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt())
        user_data['password'] = hashed_password.decode('utf-8')
        
        result = db.usuarios.insert_one(user_data)
        return str(result.inserted_id)

    @staticmethod
    def get_by_id(user_id):
        user = db.usuarios.find_one({'_id': ObjectId(user_id)})
        return user

    @staticmethod
    def get_all():
        users = list(db.usuarios.find())
        return users

    @staticmethod
    def update(user_id, update_data):
        if 'password' in update_data:
            hashed_password = bcrypt.hashpw(update_data['password'].encode('utf-8'), bcrypt.gensalt())
            update_data['password'] = hashed_password.decode('utf-8')
        
        result = db.usuarios.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})
        return result.modified_count

    @staticmethod
    def delete(user_id):
        result = db.usuarios.delete_one({'_id': ObjectId(user_id)})
        return result.deleted_count
