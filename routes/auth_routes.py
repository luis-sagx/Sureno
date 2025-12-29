"""
Authentication Routes
"""
from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from services.auth_service import AuthService
from services.user_service import UserService
from services.order_service import OrderService
from utils.decorators import login_required
from utils.response_handler import ResponseHandler


auth_routes = Blueprint('auth_routes', __name__)


@auth_routes.route('/api/auth/login', methods=['POST'])
def api_login():
    """API endpoint for user login"""
    try:
        data = request.get_json()
        
        success, result, status_code = AuthService.authenticate_user(
            data.get('email'),
            data.get('password')
        )
        
        if not success:
            return ResponseHandler.error(result, status_code)
        
        # Set session
        user_data = result
        session["user_id"] = user_data["user_id"]
        session["rol"] = user_data["rol"]
        session["user_email"] = user_data["email"]
        session["user_nombre"] = user_data["nombre"]
        session["user_apellido"] = user_data["apellido"]
        session["user_cedula"] = user_data["cedula"]
        
        # Get redirect URL
        redirect_url = AuthService.get_redirect_url(user_data["id_rol"])
        
        return jsonify({
            "message": "Inicio de sesión exitoso",
            "redirect": redirect_url
        }), 200
        
    except Exception as e:
        return ResponseHandler.server_error(str(e))


@auth_routes.route('/api/auth/register', methods=['POST'])
def api_register():
    """API endpoint for user registration"""
    try:
        data = request.form.to_dict()
        
        success, result, status_code = AuthService.register_user(data)
        
        if not success:
            return render_template('signUp.html', error=result), status_code
        
        # Redirect to login after successful registration
        return redirect(url_for('login'))
        
    except Exception as e:
        return render_template('signUp.html', error=str(e)), 500


@auth_routes.route('/api/auth/logout', methods=['POST'])
def api_logout():
    """API endpoint for user logout"""
    session.clear()
    return ResponseHandler.success(message="Sesión cerrada exitosamente")


@auth_routes.route('/api/user')
@login_required
def api_get_current_user():
    """Get current authenticated user information"""
    user_id = session.get("user_id")
    
    success, result, status_code = UserService.get_user_profile(user_id)
    
    if not success:
        return ResponseHandler.error(result, status_code)
    
    return jsonify(result), 200


@auth_routes.route('/compras')
@login_required
def compras():
    """Get user orders page"""
    user_id = session['user_id']
    
    success, pedidos, status_code = OrderService.get_user_orders(user_id)
    
    if not success:
        return jsonify({"error": pedidos}), status_code
    
    return render_template('compras.html', pedidos=pedidos)
