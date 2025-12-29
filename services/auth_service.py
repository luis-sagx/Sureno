"""
Authentication Service - Handles all authentication logic
"""
import bcrypt
from bson.objectid import ObjectId
from config import db


class AuthService:
    @staticmethod
    def authenticate_user(email, password):
        """
        Authenticate user by email and password
        Returns: (success, user_data or error_message, status_code)
        """
        if not email or not password:
            return False, "Faltan datos", 400

        user = db.usuarios.find_one({"email": email})
        if not user:
            return False, "Usuario no encontrado", 404

        if not bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
            return False, "Contraseña incorrecta", 401

        # Get role information
        role = db.roles.find_one({"id_rol": user["id_rol"]})
        if not role:
            return False, "Rol no encontrado", 500

        # Prepare user session data
        user_data = {
            "user_id": str(user["_id"]),
            "rol": role["rol"],
            "email": user.get("email", ""),
            "nombre": user.get("nombre", ""),
            "apellido": user.get("apellido", ""),
            "cedula": user.get("cedula", ""),
            "id_rol": user["id_rol"]
        }

        return True, user_data, 200

    @staticmethod
    def register_user(user_data):
        """
        Register a new user
        Returns: (success, inserted_id or error_message, status_code)
        """
        required_fields = ['email', 'nombre', 'apellido', 'password', 'cedula']
        if not all(field in user_data for field in required_fields):
            return False, "Faltan campos obligatorios", 400

        # Check if email already exists
        if db.usuarios.find_one({"email": user_data['email']}):
            return False, "El correo ya está registrado", 400

        # Get client role
        role = db.roles.find_one({"rol": "cliente"})
        if not role:
            return False, "Error en la configuración de roles", 500

        # Hash password
        hashed_password = bcrypt.hashpw(
            user_data['password'].encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')

        # Prepare user document
        new_user = {
            "email": user_data['email'],
            "nombre": user_data['nombre'],
            "apellido": user_data['apellido'],
            "password": hashed_password,
            "cedula": user_data['cedula'],
            "id_rol": role["id_rol"]
        }

        try:
            inserted_id = db.usuarios.insert_one(new_user).inserted_id
            return True, str(inserted_id), 201
        except Exception as e:
            return False, str(e), 500

    @staticmethod
    def get_redirect_url(id_rol):
        """
        Get redirect URL based on user role
        """
        if id_rol == 1:  # Cliente
            return "/index"
        elif id_rol == 2:  # Administrador
            return "/admin/home"
        else:
            return None

    @staticmethod
    def verify_session(session):
        """
        Verify if user is authenticated
        Returns: (is_authenticated, user_id or None)
        """
        user_id = session.get("user_id")
        if not user_id:
            return False, None
        return True, user_id

    @staticmethod
    def verify_admin(session):
        """
        Verify if user is admin
        Returns: (is_admin, user_id or None)
        """
        is_auth, user_id = AuthService.verify_session(session)
        if not is_auth:
            return False, None
        
        rol = session.get("rol")
        if rol != "administrador":
            return False, user_id
        
        return True, user_id
