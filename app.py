from flask import Flask, render_template, request, redirect, url_for
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from routes import register_routes
from models.user import UserModel
from routes.user_routes import user_routes 
from models.product import ProductModel
from config import db  # Asegúrate de importar la configuración de la base de datos
import bcrypt
from datetime import datetime

app = Flask(__name__)

# 🔹 Registrar Blueprint solo una vez con el prefijo '/api'
app.register_blueprint(user_routes, url_prefix='/api')
app.secret_key = "supersecreto"  

@app.route('/')
def confirmacion():
    return render_template('confirmacion.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('aboutUs.html')

@app.route('/products')
def products():
    products = ProductModel.get_all()
    for product in products:
        product['_id'] = str(product['_id'])
    return render_template('product.html', products=products)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/homeAdmin')
def home_admin():
    if "user_id" not in session or session.get("rol") != "administrador":
        return redirect(url_for("login"))
    return render_template('homeAdmin.html')

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
                
                # Redirigir según el rol
                if user["id_rol"] == 1:  # Cliente
                    return jsonify({"message": "Inicio de sesión exitoso", "redirect": "/index"}), 200
                elif user["id_rol"] == 2:  # Administrador
                    return jsonify({"message": "Inicio de sesión exitoso", "redirect": "/homeAdmin"}), 200
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
            return render_template('login')

        except Exception as e:
            return render_template('signUp', error=str(e)), 500

    return render_template('signUp')



register_routes(app)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
