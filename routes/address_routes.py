"""
Address Routes - API endpoints for address management
"""
from flask import Blueprint, request, jsonify, render_template, session
from models.address import AddressModel
from bson.objectid import ObjectId
from utils.decorators import login_required
from utils.response_handler import ResponseHandler


address_routes = Blueprint('address_routes', __name__)


@address_routes.route('/api/addresses', methods=['GET'])
@login_required
def get_addresses():
    """Get all addresses (admin only)"""
    addresses = AddressModel.get_all()
    for address in addresses:
        address['_id'] = str(address['_id'])
    return jsonify(addresses), 200


@address_routes.route('/addresses', methods=['GET'])
@login_required
def get_user_addresses():
    """Get all addresses for current user"""
    try:
        user_id = session.get("user_id")
        addresses = AddressModel.get_by_user(user_id)
        return ResponseHandler.success(data=addresses)
    except Exception as e:
        return ResponseHandler.server_error(str(e))


@address_routes.route('/addresses/<address_id>', methods=['GET'])
@login_required
def get_address(address_id):
    """Get specific address"""
    try:
        address = AddressModel.get_by_id(address_id)
        if address:
            address['_id'] = str(address['_id'])
            address['user_id'] = str(address['user_id'])
            return jsonify(address), 200
        return ResponseHandler.not_found("Dirección no encontrada")
    except Exception as e:
        return ResponseHandler.server_error(str(e))


@address_routes.route('/addresses', methods=['POST'])
@login_required
def create_address():
    """Create a new address for current user"""
    try:
        user_id = session.get("user_id")
        data = request.get_json()
        
        # Add user_id from session
        data['user_id'] = user_id
        
        inserted_id = AddressModel.create(data)
        
        return ResponseHandler.created(
            {"id": inserted_id},
            "Dirección guardada exitosamente"
        )
    except Exception as e:
        return ResponseHandler.server_error(str(e))


@address_routes.route('/addresses/<address_id>', methods=['PUT'])
@login_required
def update_address(address_id):
    """Update address"""
    try:
        update_data = request.get_json()
        modified_count = AddressModel.update(address_id, update_data)
        
        if modified_count:
            return ResponseHandler.success(message="Dirección actualizada")
        return ResponseHandler.not_found("Dirección no encontrada o sin cambios")
    except Exception as e:
        return ResponseHandler.server_error(str(e))


@address_routes.route('/addresses/<address_id>', methods=['DELETE'])
@login_required
def delete_address(address_id):
    """Delete address"""
    try:
        deleted_count = AddressModel.delete(address_id)
        
        if deleted_count:
            return ResponseHandler.success(message="Dirección eliminada")
        return ResponseHandler.not_found("Dirección no encontrada")
    except Exception as e:
        return ResponseHandler.server_error(str(e))

