import os

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_wtf.csrf import CSRFProtect, generate_csrf
from routes import register_routes
from config import db  # Asegúrate de importar la configuración de la base de datos
import bcrypt
from datetime import datetime
from bson.objectid import ObjectId
from models.address import AddressModel
from routes.order_routes import order_routes
from routes.auth import login_required, login_required_api, admin_required_api

app = Flask(__name__)

# Fix DEF-013 (RM-06): secret_key desde entorno, sin valor por defecto debil.
app.secret_key = os.environ["SECRET_KEY"]

# Fix DEF-002 (S4502): proteccion CSRF global. El token se expone en una
# cookie legible por JS (csrf_token) y el wrapper static/js/csrf.js lo reenvia
# en la cabecera X-CSRFToken de cada peticion mutante (POST/PUT/DELETE).
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

# Fix DEF-004 (S1192): literal de plantilla centralizado.
TEMPLATE_SIGNUP = 'signUp.html'

@app.route('/', methods=['GET'])
def confirmacion():
    return render_template('confirmacion.html')

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
    
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/about', methods=['GET'])
def about():
    return render_template('aboutUs.html')

@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')

@app.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos no recibidos'}), 400

        # Validar usuario autenticado
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({'error': 'Usuario no autenticado'}), 401

        # Crear documento del carrito
        cart_data = {
            "user_id": ObjectId(user_id),
            "productos": data['productos'],
            "total": data['total'],
            "fecha_creacion": datetime.now()
        }

        # Insertar en MongoDB
        result = db.carrito.insert_one(cart_data)
        return jsonify({
            'message': 'Carrito guardado',
            'id': str(result.inserted_id),
            'total': data['total']
        }), 201

    # GET: Renderizar plantilla
    return render_template('cart.html')

@app.route('/checkOut', methods=['GET', 'POST'])
@login_required
def check_out():  # Fix DEF-007 (S1542): snake_case.
    return render_template('checkOut.html')

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


@app.route('/compras', methods=['GET'])
def compras():
    # Verificar autenticación
    if 'user_id' not in session:
        return redirect(url_for('login'))
    try:
        return render_template('compras.html', pedidos=_compras_de_usuario(session['user_id']))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
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

    destino = {1: "/index", 2: "/admin/home"}.get(user["id_rol"])
    if not destino:
        return jsonify({"error": "Rol no reconocido"}), 403

    return jsonify({"message": "Inicio de sesión exitoso", "redirect": destino}), 200


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method != 'POST':
        return render_template('login.html')
    try:
        return _process_login()
    except Exception as e:
        return jsonify({"error": f"Error en el servidor: {str(e)}"}), 500


@app.route('/signUp', methods=['GET', 'POST'])
def sign_up():  # Fix DEF-007 (S1542): snake_case.
    if request.method == 'POST':
        try:
            data = request.form
            required_fields = ['email', 'nombre', 'apellido', 'password', 'cedula']
            if not all(field in data for field in required_fields):
                return render_template(TEMPLATE_SIGNUP, error="Faltan campos obligatorios"), 400

            if db.usuarios.find_one({"email": data['email']}):
                return render_template(TEMPLATE_SIGNUP, error="El correo ya está registrado"), 400

            # Obtener el id_rol correspondiente a 'cliente'
            role = db.roles.find_one({"rol": "cliente"})
            if not role:
                return render_template(TEMPLATE_SIGNUP, error="Error en la configuración de roles"), 500

            hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user_data = {
                "email": data['email'],
                "nombre": data['nombre'],
                "apellido": data['apellido'],
                "password": hashed_password,  # Contraseña hasheada
                "cedula": data['cedula'],
                "id_rol": role["id_rol"]  # Asociar el id_rol en lugar del texto
            }

            db.usuarios.insert_one(user_data)  # Fix DEF-008 (S1481): sin variable sin uso.
            return render_template('login.html')

        except Exception as e:
            return render_template(TEMPLATE_SIGNUP, error=str(e)), 500

    return render_template(TEMPLATE_SIGNUP)

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
    
@app.route('/addresses', methods=['POST'])
def create_address():
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Debes iniciar sesión"}), 401

        data = request.get_json()
        data['user_id'] = user_id  # Agregar user_id desde la sesión

        inserted_id = AddressModel.create(data)
        return jsonify({
            "message": "Dirección guardada exitosamente", 
            "id": inserted_id  # ID ya convertido a string
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# =====================================================================
# API JSON consolidada bajo /api (consumida por el frontend Astro).
# =====================================================================

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


@app.route('/api/cart', methods=['POST'])
@login_required_api
def api_cart_create():
    data = request.get_json()
    if not data or 'productos' not in data or 'total' not in data:
        return jsonify({'error': 'Datos no recibidos'}), 400
    result = db.carrito.insert_one({
        "user_id": ObjectId(session["user_id"]),
        "productos": data['productos'],
        "total": data['total'],
        "fecha_creacion": datetime.now(),
    })
    return jsonify({'message': 'Carrito guardado', 'id': str(result.inserted_id),
                    'total': data['total']}), 201


if __name__ == '__main__':
    # Fix DEF-009 (S4507): debug desactivado salvo FLASK_DEBUG=1 explicito.
    debug_mode = os.environ.get('FLASK_DEBUG') == '1'
    app.run(debug=debug_mode, use_reloader=False)
