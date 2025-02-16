from flask import Blueprint, request, jsonify, session
from bson.objectid import ObjectId
from models.order import OrderModel
from config import db
from datetime import datetime

order_routes = Blueprint('orders', __name__)

@order_routes.route('/api/orders', methods=['POST'])
def create_order():
    try:
        # Verificar autenticación
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Debes iniciar sesión"}), 401

        data = request.get_json()
        if not data:
            return jsonify({"error": "Datos inválidos"}), 400

        # Validar campos requeridos
        required_fields = ['address_id', 'cart_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Falta el campo: {field}"}), 400

        # Obtener el carrito
        cart = db.carrito.find_one({"_id": ObjectId(data['cart_id'])})
        if not cart:
            return jsonify({"error": "Carrito no encontrado"}), 404

        # Calcular total final
        total_final = cart['total'] + 3  # Añadir costo de envío

        # Crear objeto del pedido
        order_data = {
            "user_id": ObjectId(user_id),
            "address_id": ObjectId(data['address_id']),
            "cart_id": ObjectId(data['cart_id']),
            "total": total_final,
            "estado": "pendiente",
            "fecha": datetime.now()
        }

        # Guardar en la base de datos
        order_id = OrderModel.create(order_data)
        
        return jsonify({
            "message": "Pedido creado exitosamente",
            "order_id": order_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500