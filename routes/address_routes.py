from flask import Blueprint, request, jsonify, render_template
from models.address import AddressModel
from bson.objectid import ObjectId
from bson.errors import InvalidId

address_routes = Blueprint('address_routes', __name__)

@address_routes.route('/api/addresses', methods=['GET'])
def get_addresses():
    """ Obtiene todas las direcciones de la base de datos """
    addresses = AddressModel.get_all()
    for address in addresses:
        address['_id'] = str(address['_id'])
    return jsonify(addresses), 200

@address_routes.route('/addresses', methods=['GET'])
def show_addresses():
    """ Muestra las direcciones en una plantilla HTML """
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
    except Exception as e:
        return jsonify({'error': 'Error en el servidor'}), 500
    
# @address_routes.route('/addresses', methods=['POST'])
# def create_address():
#     """ Crea una nueva dirección """
#     data = request.get_json()
#     inserted_id = AddressModel.create(data)
#     return jsonify({'message': 'Dirección creada', 'id': inserted_id}), 201

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
