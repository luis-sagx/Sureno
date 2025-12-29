"""
Cart Routes - API endpoints for shopping cart
"""
from flask import Blueprint, request, session, jsonify
from services.cart_service import CartService
from utils.decorators import login_required
from utils.response_handler import ResponseHandler


cart_routes = Blueprint('cart_routes', __name__)


@cart_routes.route('/carts', methods=['GET'])
@login_required
def get_carts():
    """Get all carts"""
    carts = CartService.get_all_carts()
    return jsonify(carts), 200


@cart_routes.route('/carts/<cart_id>', methods=['GET'])
def get_cart(cart_id):
    """Get cart by ID"""
    success, result, status_code = CartService.get_cart_by_id(cart_id)
    
    if not success:
        return ResponseHandler.error(result, status_code)
    
    return jsonify(result), status_code


@cart_routes.route('/cart', methods=['POST'])
@login_required
def create_cart():
    """Create or save a cart for current user"""
    user_id = session.get("user_id")
    cart_data = request.get_json()
    
    success, result, status_code = CartService.create_cart(user_id, cart_data)
    
    if not success:
        return ResponseHandler.error(result, status_code)
    
    return jsonify(result), status_code


@cart_routes.route('/carts/<cart_id>', methods=['PUT'])
@login_required
def update_cart(cart_id):
    """Update cart"""
    update_data = request.get_json()
    
    success, result, status_code = CartService.update_cart(cart_id, update_data)
    
    if not success:
        return ResponseHandler.error(result, status_code)
    
    return ResponseHandler.success(message=result)


@cart_routes.route('/carts/<cart_id>', methods=['DELETE'])
@login_required
def delete_cart(cart_id):
    """Delete cart"""
    success, result, status_code = CartService.delete_cart(cart_id)
    
    if not success:
        return ResponseHandler.error(result, status_code)
    
    return ResponseHandler.success(message=result)

