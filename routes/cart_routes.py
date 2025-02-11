from flask import Blueprint, request, jsonify
from models.cart import CartModel
from bson.objectid import ObjectId

cart_routes = Blueprint('cart_routes', __name__)

@cart_routes.route('/api/carts', methods=['GET'])
def get_carts():
    """ Obtiene todos los carritos """
    carts = CartModel.get_all()
    for cart in carts:
        cart['_id'] = str(cart['_id'])
    return jsonify(carts), 200

@cart_routes.route('/carts/<cart_id>', methods=['GET'])
def get_cart(cart_id):
    """ Obtiene un carrito por su ID """
    cart = CartModel.get_by_id(cart_id)
    if cart:
        cart['_id'] = str(cart['_id'])
        return jsonify(cart), 200
    else:
        return jsonify({'error': 'Carrito no encontrado'}), 404

@cart_routes.route('/carts', methods=['POST'])
def create_cart():
    """ Crea un nuevo carrito """
    data = request.get_json()
    inserted_id = CartModel.create(data)
    return jsonify({'message': 'Carrito creado', 'id': inserted_id}), 201

@cart_routes.route('/carts/<cart_id>', methods=['PUT'])
def update_cart(cart_id):
    """ Actualiza un carrito existente """
    update_data = request.get_json()
    modified_count = CartModel.update(cart_id, update_data)
    if modified_count:
        return jsonify({'message': 'Carrito actualizado'}), 200
    else:
        return jsonify({'error': 'Carrito no encontrado o sin cambios'}), 404

@cart_routes.route('/carts/<cart_id>', methods=['DELETE'])
def delete_cart(cart_id):
    """ Elimina un carrito existente """
    deleted_count = CartModel.delete(cart_id)
    if deleted_count:
        return jsonify({'message': 'Carrito eliminado'}), 200
    else:
        return jsonify({'error': 'Carrito no encontrado'}), 404
