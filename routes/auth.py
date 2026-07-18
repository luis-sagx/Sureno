"""Decoradores de autenticacion y autorizacion.

Fix DEF-010 (RM-01) y DEF-011 (RM-02): proteger rutas admin y de compra.
"""
from functools import wraps

from flask import session, redirect, url_for, jsonify, request


def login_required(view):
    """Exige sesion iniciada. Si es peticion JSON responde 401, si no redirige a login."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
                return jsonify({"error": "Debes iniciar sesion"}), 401
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


def admin_required(view):
    """Exige sesion con rol administrador. Sin sesion o sin rol redirige a login (302)."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        if session.get("rol") != "administrador":
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


def login_required_api(view):
    """Como login_required pero siempre responde JSON 401 (para endpoints /api)."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "Debes iniciar sesión"}), 401
        return view(*args, **kwargs)
    return wrapper


def admin_required_api(view):
    """Exige rol administrador; responde JSON 401/403 (para endpoints /api)."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "Debes iniciar sesión"}), 401
        if session.get("rol") != "administrador":
            return jsonify({"error": "Acceso solo para administradores"}), 403
        return view(*args, **kwargs)
    return wrapper
