from flask import Flask, render_template, request, redirect, url_for
from routes import register_routes
from models.user import UserModel
from models.product import ProductModel
from config import db  # Asegúrate de importar la configuración de la base de datos
import bcrypt
from datetime import datetime

app = Flask(__name__)

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

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/singUp', methods=['GET', 'POST'])
def singUp():
    if request.method == 'POST':
        try:
            # Obtener datos del formulario (no JSON)
            data = request.form
            
            # Validar campos obligatorios
            required_fields = ['email', 'password', 'cedula', 'fecha_nacimiento']
            if not all(field in data for field in required_fields):
                return render_template('singUp.html', error="Faltan campos obligatorios"), 400
            
            # Verificar si el usuario ya existe
            if db.usuarios.find_one({"email": data['email']}):
                return render_template('singUp.html', error="El correo ya está registrado"), 400

            # Hashear la contraseña
            hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
            
            # Crear documento de usuario
            user_data = {
                "email": data['email'],
                "password": hashed_password.decode('utf-8'),
                "cedula": data['cedula'],
                "fecha_nacimiento": data['fecha_nacimiento'],
                "fecha_registro": datetime.utcnow(),
                "rol": "usuario"
            }

            # Insertar en la base de datos
            inserted_id = UserModel.create(user_data)
            return render_template('login.html')# Redirigir al login después del registro

        except Exception as e:
            return render_template('singUp.html', error=str(e)), 500
    
    # Método GET: Mostrar formulario
    return render_template('singUp.html')

register_routes(app)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
