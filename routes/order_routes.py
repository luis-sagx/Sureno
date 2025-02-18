from flask import Blueprint, request, jsonify, session
from bson.objectid import ObjectId
from models.order import OrderModel
from config import db
from datetime import datetime

order_routes = Blueprint('orders', __name__)

@order_routes.route('/api/orders', methods=['POST'])
def create_order():
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Debes iniciar sesión"}), 401

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

@order_routes.route('/api/orders', methods=['GET'])
def get_all_orders():
    try:
        orders = OrderModel.get_all()
        return jsonify(orders), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@order_routes.route('/api/orders/<order_id>', methods=['PUT'])
def update_order_status(order_id):
    try:
        data = request.get_json()
        if not data or "estado" not in data:
            return jsonify({"error": "Estado no proporcionado"}), 400

        if OrderModel.update_status(order_id, data["estado"]):
            return jsonify({"message": "Estado del pedido actualizado"}), 200
        else:
            return jsonify({"error": "Pedido no encontrado o sin cambios"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@order_routes.route('/api/orders/<order_id>', methods=['DELETE'])
def delete_order(order_id):
    try:
        # Verificar autenticación
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Debes iniciar sesión"}), 401

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