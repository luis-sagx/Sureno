from .user_routes import user_routes
from .product_routes import product_routes
from .address_routes import address_routes
from .order_routes import order_routes


def register_routes(app):
    """Registra los blueprints de la API bajo el prefijo /api."""
    app.register_blueprint(product_routes, url_prefix='/api')
    app.register_blueprint(user_routes, url_prefix='/api')
    app.register_blueprint(address_routes, url_prefix='/api')
    # order_routes se registra en app.py (también con prefijo /api).
