"""
Order Routes - API endpoints for order management
"""
from flask import Blueprint, request, jsonify, session
from services.order_service import OrderService
from utils.decorators import login_required
from utils.response_handler import ResponseHandler


order_routes = Blueprint("order_routes", __name__)


@order_routes.route('/orders', methods=['POST'])
@login_required
def create_order():
    """Create a new order"""
    user_id = session.get("user_id")
    order_data = request.get_json()
    
    if not order_data:
        return ResponseHandler.bad_request("Datos inválidos")
    
    success, result, status_code = OrderService.create_order(user_id, order_data)
    
    if not success:
        return ResponseHandler.error(result, status_code)
    
    return jsonify(result), status_code


@order_routes.route('/orders', methods=['GET'])
@login_required
def get_all_orders():
    """Get all orders"""
    success, orders, status_code = OrderService.get_all_orders()
    
    if not success:
        return ResponseHandler.error(orders, status_code)
    
    return jsonify(orders), status_code


@order_routes.route('/orders/<order_id>', methods=['PUT'])
@login_required
def update_order_status(order_id):
    """Update order status"""
    data = request.get_json()
    
    if not data or "estado" not in data:
        return ResponseHandler.bad_request("Estado no proporcionado")
    
    success, result, status_code = OrderService.update_order_status(
        order_id, 
        data["estado"]
    )
    
    if not success:
        return ResponseHandler.error(result, status_code)
    
    return ResponseHandler.success(message=result)


@order_routes.route('/orders/<order_id>', methods=['DELETE'])
@login_required
def delete_order(order_id):
    """Delete an order"""
    user_id = session.get("user_id")
    
    success, result, status_code = OrderService.delete_order(order_id, user_id)
    
    if not success:
        return ResponseHandler.error(result, status_code)
    
    return ResponseHandler.success(message=result)


@order_routes.route('/orders/<order_id>/cancelar', methods=['PUT'])
@login_required
def cancel_order(order_id):
    """Cancel an order"""
    user_id = session.get("user_id")
    
    success, result, status_code = OrderService.cancel_order(order_id, user_id)
    
    if not success:
        return ResponseHandler.error(result, status_code)
    
    return ResponseHandler.success(message=result)

def cancelar_pedido(order_id):
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Debes iniciar sesión"}), 401

        # Actualizar estado a 'cancelado'
        result = db.orders.update_one(
            {"_id": ObjectId(order_id), "user_id": ObjectId(user_id)},
            {"$set": {"estado": "cancelado"}}
        )

        if result.modified_count == 0:
            return jsonify({"error": "Pedido no encontrado o no autorizado"}), 404

        return jsonify({"message": "Pedido cancelado exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500