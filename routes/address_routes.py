from flask import Blueprint, request, jsonify, render_template, session
from models.address import AddressModel
from bson.objectid import ObjectId
from bson.errors import InvalidId
from routes.auth import login_required_api

address_routes = Blueprint('address_routes', __name__)


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

# Fix DEF-015 (RM-05): rutas relativas; el prefijo /api se aplica al registrar.
@address_routes.route('/addresses', methods=['GET'])
def get_addresses():
    """ Obtiene todas las direcciones (JSON). Ruta canonica: /api/addresses """
    addresses = AddressModel.get_all()
    for address in addresses:
        address['_id'] = str(address['_id'])
    return jsonify(addresses), 200

@address_routes.route('/addresses/view', methods=['GET'])
def show_addresses():
    """ Muestra las direcciones en una plantilla HTML. Ruta: /api/addresses/view """
    addresses = AddressModel.get_all()
    for address in addresses:
        address['_id'] = str(address['_id'])
    return render_template('address.html', addresses=addresses)

@address_routes.route('/addresses/<address_id>', methods=['GET'])
def get_address(address_id):
    try:
        object_id = ObjectId(address_id)
        address = AddressModel.get_by_id(object_id)
        if address:
            address['_id'] = str(address['_id'])
            address['user_id'] = str(address['user_id'])
            return jsonify(address), 200
        else:
            return jsonify({'error': 'Dirección no encontrada'}), 404
    except Exception:  # Fix DEF-008 (S1481): sin variable sin uso.
        return jsonify({'error': 'Error en el servidor'}), 500

@address_routes.route('/addresses/<address_id>', methods=['PUT'])
def update_address(address_id):
    """ Actualiza una dirección existente """
    update_data = request.get_json()
    modified_count = AddressModel.update(address_id, update_data)
    if modified_count:
        return jsonify({'message': 'Dirección actualizada'}), 200
    else:
        return jsonify({'error': 'Dirección no encontrada o sin cambios'}), 404

@address_routes.route('/addresses/<address_id>', methods=['DELETE'])
def delete_address(address_id):
    """ Elimina una dirección existente """
    deleted_count = AddressModel.delete(address_id)
    if deleted_count:
        return jsonify({'message': 'Dirección eliminada'}), 200
    else:
        return jsonify({'error': 'Dirección no encontrada'}), 404
