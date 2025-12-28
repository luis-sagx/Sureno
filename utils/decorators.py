"""
Decorators for authentication and authorization
"""
from functools import wraps
from flask import session, jsonify, redirect, url_for, request


def login_required(f):
    """
    Decorator to require user authentication.
    Works for both API and web routes.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            # Check if it's an API request (JSON) or web request
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({"error": "No hay usuario autenticado"}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator to require admin role.
    Works for both API and web routes.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        rol = session.get('rol')
        
        if not user_id:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({"error": "No hay usuario autenticado"}), 401
            return redirect(url_for('login'))
        
        if rol != 'administrador':
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({"error": "No tienes permisos de administrador"}), 403
            return "Acceso denegado", 403
            
        return f(*args, **kwargs)
    return decorated_function


def json_required(f):
    """
    Decorator to ensure request has JSON content
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({"error": "Content-Type debe ser application/json"}), 400
        return f(*args, **kwargs)
    return decorated_function
