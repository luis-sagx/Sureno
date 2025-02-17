from flask import Blueprint
from .user_routes import user_routes
from .product_routes import product_routes
from .admin_routes import admin_routes
from .order_routes import order_routes

def register_routes(app):
    app.register_blueprint(product_routes, url_prefix='/api')
    # 🔹 Registrar Blueprint solo una vez con el prefijo '/api'
    app.register_blueprint(user_routes, url_prefix='/api')
    app.register_blueprint(admin_routes, url_prefix='/admin')  # Registrar admin_routes con prefijo '/admin'
    app.secret_key = "supersecreto"
