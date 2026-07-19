import os

from flask import Flask, request, session, jsonify
from flask_wtf.csrf import CSRFProtect, generate_csrf
from routes import register_routes
from config import db
import bcrypt
from datetime import datetime
from bson.objectid import ObjectId
from routes.order_routes import order_routes
from routes.auth import login_required_api, admin_required_api

app = Flask(__name__)

# Fix DEF-013 (RM-06): secret_key desde entorno, sin valor por defecto debil.
app.secret_key = os.environ["SECRET_KEY"]

# Fix DEF-002 (S4502): proteccion CSRF global. El token se expone en una cookie
# legible por JS (csrf_token) y el frontend Astro lo reenvia en la cabecera
# X-CSRFToken de cada peticion mutante (POST/PUT/DELETE).
app.config['WTF_CSRF_TIME_LIMIT'] = None
csrf = CSRFProtect(app)


@app.after_request
def set_csrf_cookie(response):
    response.set_cookie(
        'csrf_token', generate_csrf(),
        secure=os.environ.get('FLASK_DEBUG') != '1',
        httponly=False, samesite='Lax'
    )
    return response


app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
# Fix DEF-015 (RM-05): prefijo /api en un solo lugar; rutas del blueprint relativas.
app.register_blueprint(order_routes, url_prefix='/api')
register_routes(app)


# =====================================================================
# API JSON pura. La UI la sirve el frontend Astro (frontend/).
# =====================================================================

@app.route('/api/user', methods=['GET'])
def api_user():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "No hay usuario autenticado"}), 401

    user = db.usuarios.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({
        "email": user.get("email", ""),
        "nombre": user.get("nombre", ""),
        "apellido": user.get("apellido", ""),
        "cedula": user.get("cedula", ""),
        "rol": session.get("rol", "")
    })


def _compras_de_usuario(user_id):
    """Pedidos del usuario con carrito y dirección resueltos, ordenados por fecha desc."""
    pipeline = [
        {"$match": {"user_id": ObjectId(user_id)}},
        {"$lookup": {"from": "carrito", "localField": "cart_id",
                     "foreignField": "_id", "as": "carrito_info"}},
        {"$unwind": "$carrito_info"},
        {"$lookup": {"from": "addresses", "localField": "address_id",
                     "foreignField": "_id", "as": "direccion_info"}},
        {"$unwind": "$direccion_info"},
        {"$sort": {"fecha": -1}},
        {"$project": {
            "_id": 0,
            "id": {"$toString": "$_id"},
            "fecha_formateada": {"$dateToString": {"format": "%d/%m/%Y %H:%M", "date": "$fecha"}},
            "total": 1,
            "estado": 1,
            "productos": "$carrito_info.productos",
            "direccion": {
                "provincia": "$direccion_info.provincia",
                "canton": "$direccion_info.canton",
                "parroquia": "$direccion_info.parroquia",
            },
        }},
    ]
    pedidos = list(db.orders.aggregate(pipeline))
    for pedido in pedidos:
        pedido['total'] = f"${pedido['total']:.2f}"
    return pedidos


def _start_session(user, role):
    """Guarda los datos de sesion tras un login valido."""
    session["user_id"] = str(user["_id"])
    session["rol"] = role["rol"]
    session["user_email"] = user.get("email", "")
    session["user_nombre"] = user.get("nombre", "")
    session["user_apellido"] = user.get("apellido", "")
    session["user_cedula"] = user.get("cedula", "")


def _process_login():
    """Valida credenciales y arranca la sesion. Fix DEF-003 (S3776): guard clauses."""
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Faltan datos"}), 400

    user = db.usuarios.find_one({"email": data["email"]})
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    if not bcrypt.checkpw(data["password"].encode('utf-8'), user["password"].encode('utf-8')):
        return jsonify({"error": "Contraseña incorrecta"}), 401

    role = db.roles.find_one({"id_rol": user["id_rol"]})
    if not role:
        return jsonify({"error": "Rol no encontrado"}), 500

    _start_session(user, role)

    destino = {1: "/", 2: "/admin/home"}.get(user["id_rol"])
    if not destino:
        return jsonify({"error": "Rol no reconocido"}), 403

    return jsonify({"message": "Inicio de sesión exitoso", "redirect": destino}), 200


@app.route('/api/csrf', methods=['GET'])
def api_csrf():
    """Devuelve el token CSRF y (vía after_request) siembra la cookie csrf_token."""
    return jsonify({"csrfToken": generate_csrf()}), 200


@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        return _process_login()
    except Exception as e:
        return jsonify({"error": f"Error en el servidor: {str(e)}"}), 500


@app.route('/api/signup', methods=['POST'])
def api_signup():
    try:
        data = request.get_json() or {}
        required = ['email', 'nombre', 'apellido', 'password', 'cedula']
        if not all(f in data and data[f] for f in required):
            return jsonify({"error": "Faltan campos obligatorios"}), 400

        if db.usuarios.find_one({"email": data['email']}):
            return jsonify({"error": "El correo ya está registrado"}), 409

        role = db.roles.find_one({"rol": "cliente"})
        if not role:
            return jsonify({"error": "Error en la configuración de roles"}), 500

        hashed = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db.usuarios.insert_one({
            "email": data['email'], "nombre": data['nombre'], "apellido": data['apellido'],
            "password": hashed, "cedula": data['cedula'], "id_rol": role["id_rol"],
        })
        return jsonify({"message": "Registro exitoso", "redirect": "/login"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"message": "Sesión cerrada"}), 200


@app.route('/api/cart/<cart_id>', methods=['GET'])
def get_cart(cart_id):
    try:
        cart = db.carrito.find_one({"_id": ObjectId(cart_id)})
        if not cart:
            return jsonify({"error": "Carrito no encontrado"}), 404

        return jsonify({
            "_id": str(cart["_id"]),
            "total": cart["total"],
            "productos": cart["productos"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/cart', methods=['POST'])
@login_required_api
def api_cart_create():
    # Fix CP-24: el precio/total del cliente no es de confianza (se puede
    # manipular en el DOM/localStorage). El servidor recalcula cada linea
    # y el total a partir del precio real en Mongo; el payload del cliente
    # solo se usa para saber que producto y cuantas unidades quiere.
    data = request.get_json()
    if not data or 'productos' not in data or not isinstance(data['productos'], list) or not data['productos']:
        return jsonify({'error': 'Datos no recibidos'}), 400

    productos = []
    total = 0
    for item in data['productos']:
        cantidad = item.get('cantidad')
        if not isinstance(cantidad, (int, float)) or cantidad <= 0:
            return jsonify({'error': 'Cantidad invalida'}), 400
        try:
            producto = db.productos.find_one({"_id": ObjectId(item.get('id'))})
        except Exception:
            producto = None
        if not producto:
            return jsonify({'error': f"Producto no encontrado: {item.get('id')}"}), 404

        precio_real = producto['precio']
        total += precio_real * cantidad
        productos.append({**item, "precio": precio_real})

    result = db.carrito.insert_one({
        "user_id": ObjectId(session["user_id"]),
        "productos": productos,
        "total": total,
        "fecha_creacion": datetime.now(),
    })
    return jsonify({'message': 'Carrito guardado', 'id': str(result.inserted_id),
                    'total': total}), 201


@app.route('/api/compras', methods=['GET'])
@login_required_api
def api_compras():
    try:
        return jsonify(_compras_de_usuario(session["user_id"])), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/admin/orders/<order_id>', methods=['DELETE'])
@admin_required_api
def api_admin_delete_order(order_id):
    """Elimina cualquier pedido (solo admin), sin la restricción de propietario."""
    if not ObjectId.is_valid(order_id):
        return jsonify({"error": "ID inválido"}), 400
    result = db.orders.delete_one({"_id": ObjectId(order_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Pedido no encontrado"}), 404
    return jsonify({"message": "Pedido eliminado"}), 200


@app.route('/api/admin/stats', methods=['GET'])
@admin_required_api
def api_admin_stats():
    return jsonify({
        "total_clientes": db.usuarios.count_documents({}),
        "total_productos": db.productos.count_documents({}),
        "total_pedidos": db.orders.count_documents({}),
    }), 200


if __name__ == '__main__':
    # Fix DEF-009 (S4507): debug desactivado salvo FLASK_DEBUG=1 explicito.
    debug_mode = os.environ.get('FLASK_DEBUG') == '1'
    app.run(debug=debug_mode, use_reloader=False)
