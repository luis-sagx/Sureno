from flask import Blueprint, request, jsonify, session
from bson.objectid import ObjectId
from models.order import OrderModel
from config import db
from datetime import datetime
from routes.auth import admin_required_api

order_routes = Blueprint("orders", __name__)

# Fix DEF-005 (S1192): literal centralizado.
MSG_LOGIN_REQUERIDO = "Debes iniciar sesión"

# Estados válidos de un pedido (evita inyectar valores arbitrarios).
ESTADOS_VALIDOS = {"pendiente", "pagado", "enviado", "entregado", "cancelado"}


# Fix DEF-015 (RM-05): rutas relativas; el prefijo /api se define al registrar.
@order_routes.route('/orders', methods=['POST'])
def create_order():
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": MSG_LOGIN_REQUERIDO}), 401

        data = request.get_json()
        if not data:
            return jsonify({"error": "Datos inválidos"}), 400

        required_fields = ['address_id', 'cart_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Falta el campo: {field}"}), 400

        cart = db.carrito.find_one({"_id": ObjectId(data['cart_id'])})
        if not cart:
            return jsonify({"error": "Carrito no encontrado"}), 404

        # Fix DEF-019: bloquear pedidos de un carrito sin productos.
        if not cart.get('productos'):
            return jsonify({"error": "El carrito está vacío"}), 400

        total_final = cart['total'] + 3  # Añadir costo de envío

        order_data = { 
            "user_id": ObjectId(user_id),
            "address_id": ObjectId(data['address_id']),
            "cart_id": ObjectId(data['cart_id']),
            "total": total_final,
            "estado": "pendiente",
            "fecha": datetime.now()
        }

        order_id = OrderModel.create(order_data)
        
        return jsonify({
            "message": "Pedido creado exitosamente",
            "order_id": order_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@order_routes.route('/orders', methods=['GET'])
@admin_required_api
def get_all_orders():
    """Lista todos los pedidos (solo admin)."""
    try:
        orders = OrderModel.get_all()
        return jsonify(orders), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@order_routes.route('/orders/<order_id>', methods=['PUT'])
@admin_required_api
def update_order_status(order_id):
    """Cambia el estado de un pedido (solo admin, estado validado)."""
    try:
        data = request.get_json()
        if not data or "estado" not in data:
            return jsonify({"error": "Estado no proporcionado"}), 400

        if data["estado"] not in ESTADOS_VALIDOS:
            return jsonify({"error": "Estado inválido"}), 400

        if OrderModel.update_status(order_id, data["estado"]):
            return jsonify({"message": "Estado del pedido actualizado"}), 200
        else:
            return jsonify({"error": "Pedido no encontrado o sin cambios"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@order_routes.route('/orders/<order_id>', methods=['DELETE'])
def delete_order(order_id):
    try:
        # Verificar autenticación
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": MSG_LOGIN_REQUERIDO}), 401

        # Validar formato del ID
        if not ObjectId.is_valid(order_id):
            return jsonify({"error": "ID inválido"}), 400

        # Eliminar de MongoDB
        result = db.orders.delete_one({
            "_id": ObjectId(order_id),
            "user_id": ObjectId(user_id)
        })

        if result.deleted_count == 0:
            return jsonify({"error": "Pedido no encontrado o no autorizado"}), 404

        return jsonify({"message": "Pedido eliminado exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500
    
@order_routes.route('/orders/<order_id>/cancelar', methods=['PUT'])
def cancelar_pedido(order_id):
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": MSG_LOGIN_REQUERIDO}), 401

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