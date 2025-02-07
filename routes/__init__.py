# routes/__init__.py

from .product_routes import product_routes
# Si tienes más blueprints, impórtalos también:
# from .user_routes import user_routes
# from .address_routes import address_routes
# from .order_routes import order_routes
# etc.

def register_routes(app):
    """
    Función que registra todos los blueprints de rutas en la aplicación Flask.
    """
    app.register_blueprint(product_routes)
    # Registra otros blueprints, por ejemplo:
    # app.register_blueprint(user_routes)
    # app.register_blueprint(address_routes)
    # app.register_blueprint(order_routes)
