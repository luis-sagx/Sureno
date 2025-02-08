from flask import Blueprint, request, jsonify, render_template
from models.user import UserModel
from bson.objectid import ObjectId
import os
from werkzeug.utils import secure_filename

user_routes = Blueprint('user_routes', __name__)

# Configuración de carpeta de subida
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@user_routes.route('/api/users', methods=['GET'])
def get_users():
    # Obtén la lista de productos desde la base de datos
    users = UserModel.get_all()  # Cambiado: get_all() en lugar de get_all_products()
    # Convierte el ObjectId a string para que JSON sea serializable
    for user in users:
        user['_id'] = str(user['_id'])
    return jsonify(users), 200

@user_routes.route('/users', methods=['GET'])
def show_users():
    # Obtén la lista de productos desde la base de datos
    users = UserModel.get_all()  # Asegúrate de llamar al método correcto
    # Convertir ObjectId a string para evitar problemas en la plantilla
    for user in users:
        user['_id'] = str(user['_id'])
    # Agrega un print para verificar el contenido
    print("Productos obtenidos:", users)
    # Pasa los productos a la plantilla product.html
    return render_template('user.html', users=users)

@user_routes.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """
    Devuelve un producto específico dado su id.
    """
    user = UserModel.get_by_id(user_id)  # Usamos get_by_id()
    if user:
        user['_id'] = str(user['_id'])
        return jsonify(user), 200
    else:
        return jsonify({'error': 'Producto no encontrado'}), 404

@user_routes.route('/users', methods=['POST'])
def create_user():
    """
    Crea un nuevo producto.
    Se espera que la petición incluya un JSON con la información del producto.
    """
    data = request.get_json()
    # Aquí podrías validar los datos recibidos antes de insertar
    inserted_id = UserModel.create(data)  # Usamos create() en lugar de create_product()
    return jsonify({'message': 'Usuario creado', 'id': inserted_id}), 201

@user_routes.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """
    Actualiza los datos de un producto existente.
    """
    update_data = request.get_json()
    modified_count = UserModel.update(user_id, update_data)  # Usamos update() en lugar de update_product()
    if modified_count:
        return jsonify({'message': 'Usuario actualizado'}), 200
    else:
        return jsonify({'error': 'Producto no encontrado o no hubo cambios'}), 404

@user_routes.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Elimina un producto existente.
    """
    deleted_count = UserModel.delete(user_id)  # Usamos delete() en lugar de delete_product()
    if deleted_count:
        return jsonify({'message': 'User eliminado'}), 200
    else:
        return jsonify({'error': 'User no encontrado'}), 404
