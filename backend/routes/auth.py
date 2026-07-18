"""Decoradores de autorizacion para la API JSON.

Fix DEF-010 (RM-01) y DEF-011 (RM-02): proteger endpoints de admin y de compra.
El control de acceso de la UI vive en el middleware del frontend Astro; estos
decoradores protegen la API en el backend.
"""
from functools import wraps

from flask import session, jsonify


def login_required_api(view):
    """Exige sesion iniciada; responde JSON 401 si falta."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "Debes iniciar sesión"}), 401
        return view(*args, **kwargs)
    return wrapper


def admin_required_api(view):
    """Exige rol administrador; responde JSON 401/403."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "Debes iniciar sesión"}), 401
        if session.get("rol") != "administrador":
            return jsonify({"error": "Acceso solo para administradores"}), 403
        return view(*args, **kwargs)
    return wrapper
