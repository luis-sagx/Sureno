"""
User Routes - API endpoints for user management
"""
from flask import Blueprint, request, jsonify, render_template
from services.user_service import UserService
from utils.response_handler import ResponseHandler
from utils.decorators import admin_required


user_routes = Blueprint('user_routes', __name__)


@user_routes.route('/api/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users (API)"""
    users = UserService.get_all_users()
    return jsonify(users), 200


@user_routes.route('/users', methods=['GET'])
@admin_required
def show_users():
    """Show users page"""
    users = UserService.get_all_users()
    return render_template('user.html', users=users)


@user_routes.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    success, result, status_code = UserService.get_user_by_id(user_id)
    
    if not success:
        return ResponseHandler.error(result, status_code)
    
    return jsonify(result), status_code


@user_routes.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.get_json()
    
    success, result, status_code = UserService.create_user(data)
    
    if not success:
        return ResponseHandler.error(result, status_code)
    
    return ResponseHandler.created({'id': result}, 'Usuario creado')


@user_routes.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user information"""
    update_data = request.get_json()
    
    success, result, status_code = UserService.update_user(user_id, update_data)
    
    if not success:
        return ResponseHandler.error(result, status_code)
    
    return ResponseHandler.success(message=result)


@user_routes.route('/users/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete user"""
    success, result, status_code = UserService.delete_user(user_id)
    
    if not success:
        return ResponseHandler.error(result, status_code)
    
    return ResponseHandler.success(message=result)

