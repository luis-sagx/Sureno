"""
Routes Registration
"""
from flask import Blueprint
from .auth_routes import auth_routes
from .user_routes import user_routes
from .product_routes import product_routes
from .admin_routes import admin_routes
from .address_routes import address_routes
from .order_routes import order_routes
from .cart_routes import cart_routes


def register_routes(app):
    """Register all application blueprints"""
    
    # Set secret key for sessions
    app.secret_key = app.config.get('SECRET_KEY', 'supersecreto')
    
    # Register blueprints with appropriate prefixes
    app.register_blueprint(auth_routes)  # No prefix for auth routes
    app.register_blueprint(user_routes, url_prefix='/api')
    app.register_blueprint(product_routes, url_prefix='/api')
    app.register_blueprint(cart_routes, url_prefix='/api')
    app.register_blueprint(order_routes, url_prefix='/api')
    app.register_blueprint(address_routes, url_prefix='/api')
    app.register_blueprint(admin_routes, url_prefix='/admin')

