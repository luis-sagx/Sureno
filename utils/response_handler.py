"""
Response Handler - Standardized API responses
"""
from flask import jsonify


class ResponseHandler:
    """Utility class for standardized API responses"""

    @staticmethod
    def success(data=None, message=None, status_code=200):
        """
        Generate success response
        """
        response = {"success": True}
        
        if message:
            response["message"] = message
        
        if data is not None:
            response["data"] = data
        
        return jsonify(response), status_code

    @staticmethod
    def error(message, status_code=400, errors=None):
        """
        Generate error response
        """
        response = {
            "success": False,
            "error": message
        }
        
        if errors:
            response["errors"] = errors
        
        return jsonify(response), status_code

    @staticmethod
    def created(data, message="Recurso creado exitosamente"):
        """
        Generate created response (201)
        """
        return ResponseHandler.success(data=data, message=message, status_code=201)

    @staticmethod
    def not_found(message="Recurso no encontrado"):
        """
        Generate not found response (404)
        """
        return ResponseHandler.error(message=message, status_code=404)

    @staticmethod
    def unauthorized(message="No autorizado"):
        """
        Generate unauthorized response (401)
        """
        return ResponseHandler.error(message=message, status_code=401)

    @staticmethod
    def forbidden(message="Acceso prohibido"):
        """
        Generate forbidden response (403)
        """
        return ResponseHandler.error(message=message, status_code=403)

    @staticmethod
    def bad_request(message="Solicitud inválida", errors=None):
        """
        Generate bad request response (400)
        """
        return ResponseHandler.error(message=message, status_code=400, errors=errors)

    @staticmethod
    def server_error(message="Error interno del servidor"):
        """
        Generate server error response (500)
        """
        return ResponseHandler.error(message=message, status_code=500)
