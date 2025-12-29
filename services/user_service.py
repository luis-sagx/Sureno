"""
User Service - Handles user business logic
"""
from bson.objectid import ObjectId
from models.user import UserModel


class UserService:
    @staticmethod
    def get_all_users():
        """Get all users"""
        users = UserModel.get_all()
        for user in users:
            user['_id'] = str(user['_id'])
        return users

    @staticmethod
    def get_user_by_id(user_id):
        """
        Get user by ID
        Returns: (success, user_data or error_message, status_code)
        """
        try:
            user = UserModel.get_by_id(user_id)
            if user:
                user['_id'] = str(user['_id'])
                return True, user, 200
            return False, "Usuario no encontrado", 404
        except Exception as e:
            return False, str(e), 500

    @staticmethod
    def create_user(user_data):
        """
        Create a new user
        Returns: (success, inserted_id or error_message, status_code)
        """
        try:
            inserted_id = UserModel.create(user_data)
            return True, inserted_id, 201
        except Exception as e:
            return False, str(e), 500

    @staticmethod
    def update_user(user_id, update_data):
        """
        Update user information
        Returns: (success, message or error_message, status_code)
        """
        try:
            modified_count = UserModel.update(user_id, update_data)
            if modified_count:
                return True, "Usuario actualizado", 200
            return False, "Usuario no encontrado o no hubo cambios", 404
        except Exception as e:
            return False, str(e), 500

    @staticmethod
    def delete_user(user_id):
        """
        Delete user
        Returns: (success, message or error_message, status_code)
        """
        try:
            deleted_count = UserModel.delete(user_id)
            if deleted_count:
                return True, "Usuario eliminado", 200
            return False, "Usuario no encontrado", 404
        except Exception as e:
            return False, str(e), 500

    @staticmethod
    def get_user_profile(user_id):
        """
        Get user profile information for API
        Returns: (success, profile_data or error_message, status_code)
        """
        try:
            user = UserModel.get_by_id(user_id)
            if not user:
                return False, "Usuario no encontrado", 404

            profile = {
                "email": user.get("email", ""),
                "nombre": user.get("nombre", ""),
                "apellido": user.get("apellido", ""),
                "cedula": user.get("cedula", "")
            }
            return True, profile, 200
        except Exception as e:
            return False, str(e), 500
