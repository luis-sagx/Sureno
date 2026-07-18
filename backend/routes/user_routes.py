from flask import Blueprint, request, jsonify
from models.user import UserModel
from routes.auth import admin_required_api

user_routes = Blueprint('user_routes', __name__)

# Campos sensibles que nunca se exponen en la API.
_SENSITIVE = ('password',)


def _sanitize(user):
    user['_id'] = str(user['_id'])
    for field in _SENSITIVE:
        user.pop(field, None)
    return user


# Fix DEF-015 (RM-05): rutas relativas; el prefijo /api se aplica al registrar.
# Seguridad: la gestión de usuarios es solo para administradores y nunca
# devuelve el hash de contraseña (info disclosure / IDOR).
@user_routes.route('/users', methods=['GET'])
@admin_required_api
def get_users():
    """Lista de usuarios (solo admin, sin campos sensibles)."""
    return jsonify([_sanitize(u) for u in UserModel.get_all()]), 200


@user_routes.route('/users/<user_id>', methods=['GET'])
@admin_required_api
def get_user(user_id):
    """Usuario por id (solo admin, sin campos sensibles)."""
    user = UserModel.get_by_id(user_id)
    if user:
        return jsonify(_sanitize(user)), 200
    return jsonify({'error': 'Usuario no encontrado'}), 404


@user_routes.route('/users', methods=['POST'])
@admin_required_api
def create_user():
    """Crea un usuario (solo admin)."""
    data = request.get_json()
    inserted_id = UserModel.create(data)
    return jsonify({'message': 'Usuario creado', 'id': inserted_id}), 201


@user_routes.route('/users/<user_id>', methods=['PUT'])
@admin_required_api
def update_user(user_id):
    """Actualiza un usuario (solo admin). No permite cambiar rol ni contraseña por esta vía."""
    update_data = request.get_json() or {}
    for prohibido in ('id_rol', 'password'):
        update_data.pop(prohibido, None)
    modified_count = UserModel.update(user_id, update_data)
    if modified_count:
        return jsonify({'message': 'Usuario actualizado'}), 200
    return jsonify({'error': 'Usuario no encontrado o sin cambios'}), 404


@user_routes.route('/users/<user_id>', methods=['DELETE'])
@admin_required_api
def delete_user(user_id):
    """Elimina un usuario (solo admin)."""
    deleted_count = UserModel.delete(user_id)
    if deleted_count:
        return jsonify({'message': 'Usuario eliminado'}), 200
    return jsonify({'error': 'Usuario no encontrado'}), 404
