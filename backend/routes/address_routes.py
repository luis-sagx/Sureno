from flask import Blueprint, request, jsonify, session
from models.address import AddressModel
from config import db
from bson.objectid import ObjectId
from routes.auth import login_required_api, admin_required_api

address_routes = Blueprint('address_routes', __name__)


def _es_admin():
    return session.get("rol") == "administrador"


def _puede_acceder(address):
    """El dueño de la dirección o un administrador."""
    return _es_admin() or str(address.get("user_id")) == session.get("user_id")


@address_routes.route('/addresses', methods=['POST'])
@login_required_api
def create_address():
    """Crea una dirección para el usuario en sesión. Ruta canónica: /api/addresses (POST)."""
    try:
        data = request.get_json() or {}
        data['user_id'] = session["user_id"]
        inserted_id = AddressModel.create(data)
        return jsonify({"message": "Dirección guardada exitosamente", "id": inserted_id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Listar todas las direcciones es una operación administrativa (info disclosure).
@address_routes.route('/addresses', methods=['GET'])
@admin_required_api
def get_addresses():
    """Lista todas las direcciones (solo admin)."""
    addresses = AddressModel.get_all()
    for address in addresses:
        address['_id'] = str(address['_id'])
    return jsonify(addresses), 200


@address_routes.route('/addresses/<address_id>', methods=['GET'])
@login_required_api
def get_address(address_id):
    """Detalle de una dirección: solo su dueño o un admin (evita IDOR)."""
    try:
        object_id = ObjectId(address_id)
    except Exception:
        return jsonify({'error': 'ID inválido'}), 400

    address = AddressModel.get_by_id(object_id)
    if not address:
        return jsonify({'error': 'Dirección no encontrada'}), 404
    if not _puede_acceder(address):
        return jsonify({'error': 'No autorizado'}), 403

    address['_id'] = str(address['_id'])
    address['user_id'] = str(address['user_id'])
    return jsonify(address), 200


@address_routes.route('/addresses/<address_id>', methods=['PUT'])
@login_required_api
def update_address(address_id):
    """Actualiza una dirección: solo su dueño o un admin."""
    try:
        object_id = ObjectId(address_id)
    except Exception:
        return jsonify({'error': 'ID inválido'}), 400

    address = db.addresses.find_one({"_id": object_id})
    if not address:
        return jsonify({'error': 'Dirección no encontrada'}), 404
    if not _puede_acceder(address):
        return jsonify({'error': 'No autorizado'}), 403

    update_data = request.get_json() or {}
    update_data.pop('user_id', None)  # no se permite reasignar dueño
    result = db.addresses.update_one({"_id": object_id}, {"$set": update_data})
    if result.modified_count:
        return jsonify({'message': 'Dirección actualizada'}), 200
    return jsonify({'error': 'Dirección sin cambios'}), 404


@address_routes.route('/addresses/<address_id>', methods=['DELETE'])
@login_required_api
def delete_address(address_id):
    """Elimina una dirección: solo su dueño o un admin."""
    try:
        object_id = ObjectId(address_id)
    except Exception:
        return jsonify({'error': 'ID inválido'}), 400

    filtro = {"_id": object_id}
    if not _es_admin():
        filtro["user_id"] = ObjectId(session["user_id"])
    result = db.addresses.delete_one(filtro)
    if result.deleted_count:
        return jsonify({'message': 'Dirección eliminada'}), 200
    return jsonify({'error': 'Dirección no encontrada o no autorizada'}), 404
