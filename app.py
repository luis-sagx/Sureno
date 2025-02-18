from flask import Flask, render_template, request, redirect, url_for
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Blueprint
from routes import register_routes
from routes.user_routes import user_routes 
from config import db  # Asegúrate de importar la configuración de la base de datos
import bcrypt
from datetime import datetime
from bson.objectid import ObjectId
from models.cart import CartModel
from models.address import AddressModel 
from routes.order_routes import order_routes

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
app.register_blueprint(order_routes)
register_routes(app)

@app.route('/')
def confirmacion():
    return render_template('confirmacion.html')

@app.route('/api/user')
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
        "cedula": user.get("cedula", "")
    })
    
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('aboutUs.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/cart', methods=['GET', 'POST'])
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
def checkOut():
    return render_template('checkOut.html')

@app.route('/compras')
def compras():
    # Verificar autenticación
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    try:
        # Pipeline de agregación
        pipeline = [
            # Paso 1: Filtrar órdenes del usuario actual
            {
                "$match": {
                    "user_id": ObjectId(user_id)
                }
            },
            # Paso 2: Buscar información del carrito
            {
                "$lookup": {
                    "from": "carrito",
                    "localField": "cart_id",
                    "foreignField": "_id",
                    "as": "carrito_info"
                }
            },
            # Paso 3: Descomponer el array de carrito
            {
                "$unwind": "$carrito_info"
            },
            # Paso 4: Buscar información de la dirección
            {
                "$lookup": {
                    "from": "addresses",
                    "localField": "address_id",
                    "foreignField": "_id",
                    "as": "direccion_info"
                }
            },
            # Paso 5: Descomponer el array de dirección
            {
                "$unwind": "$direccion_info"
            },
            # Paso 6: Ordenar por fecha descendente
            {
                "$sort": {"fecha": -1}
            },
            # Paso 7: Proyectar los campos necesarios
            {
                "$project": {
                    "_id": 0,
                    "fecha_formateada": {
                        "$dateToString": {
                            "format": "%d/%m/%Y %H:%M",
                            "date": "$fecha"
                        }
                    },
                    "total": 1,
                    "estado": 1,
                    "productos": "$carrito_info.productos",
                    "direccion": {
                        "provincia": "$direccion_info.provincia",
                        "canton": "$direccion_info.canton",
                        "parroquia": "$direccion_info.parroquia"
                    }
                }
            }
        ]

        # Ejecutar la consulta
        pedidos = list(db.orders.aggregate(pipeline))
        
        # Formatear precios
        for pedido in pedidos:
            pedido['total'] = f"${pedido['total']:.2f}"
            
        return render_template('compras.html', pedidos=pedidos)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data or "email" not in data or "password" not in data:
                return jsonify({"error": "Faltan datos"}), 400

            user = db.usuarios.find_one({"email": data["email"]})
            if not user:
                return jsonify({"error": "Usuario no encontrado"}), 404

            if bcrypt.checkpw(data["password"].encode('utf-8'), user["password"].encode('utf-8')):
                role = db.roles.find_one({"id_rol": user["id_rol"]})

                if not role:
                    return jsonify({"error": "Rol no encontrado"}), 500

                session["user_id"] = str(user["_id"])
                session["rol"] = role["rol"]
                
                session["user_email"] = user.get("email", "")
                session["user_nombre"] = user.get("nombre", "")
                session["user_apellido"] = user.get("apellido", "")
                session["user_cedula"] = user.get("cedula", "")
                
                # Redirigir según el rol
                if user["id_rol"] == 1:  # Cliente
                    return jsonify({"message": "Inicio de sesión exitoso", "redirect": "/index"}), 200
                elif user["id_rol"] == 2:  # Administrador
                    return jsonify({"message": "Inicio de sesión exitoso", "redirect": "/admin/home"}), 200
                else:
                    return jsonify({"error": "Rol no reconocido"}), 403

            return jsonify({"error": "Contraseña incorrecta"}), 401

        except Exception as e:
            return jsonify({"error": f"Error en el servidor: {str(e)}"}), 500

    return render_template('login.html')

@app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        try:
            data = request.form
            required_fields = ['email', 'nombre', 'apellido', 'password', 'cedula']
            if not all(field in data for field in required_fields):
                return render_template('signUp.html', error="Faltan campos obligatorios"), 400

            if db.usuarios.find_one({"email": data['email']}):
                return render_template('signUp.html', error="El correo ya está registrado"), 400

            # Obtener el id_rol correspondiente a 'cliente'
            role = db.roles.find_one({"rol": "cliente"})
            if not role:
                return render_template('signUp.html', error="Error en la configuración de roles"), 500

            hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user_data = {
                "email": data['email'],
                "nombre": data['nombre'],
                "apellido": data['apellido'],
                "password": hashed_password,  # Contraseña hasheada
                "cedula": data['cedula'],
                "id_rol": role["id_rol"]  # Asociar el id_rol en lugar del texto
            }

            inserted_id = db.usuarios.insert_one(user_data).inserted_id
            return render_template('login.html')

        except Exception as e:
            return render_template('signUp.html', error=str(e)), 500

    return render_template('signUp.html')

print("Colecciones disponibles en la BD:", db.list_collection_names()) 

@app.route('/api/cart/<cart_id>')
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
    
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
