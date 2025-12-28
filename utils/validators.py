"""
Validators - Input validation utilities
"""
import re


class Validator:
    """Utility class for common validations"""

    @staticmethod
    def validate_email(email):
        """
        Validate email format
        Returns: (is_valid, error_message or None)
        """
        if not email:
            return False, "Email es requerido"
        
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return False, "Formato de email inválido"
        
        return True, None

    @staticmethod
    def validate_password(password):
        """
        Validate password strength
        Returns: (is_valid, error_message or None)
        """
        if not password:
            return False, "Contraseña es requerida"
        
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        
        return True, None

    @staticmethod
    def validate_required_fields(data, required_fields):
        """
        Validate that all required fields are present
        Returns: (is_valid, missing_fields or None)
        """
        missing = [field for field in required_fields if field not in data or not data[field]]
        if missing:
            return False, missing
        return True, None

    @staticmethod
    def validate_cedula(cedula):
        """
        Validate Ecuadorian cedula format (10 digits)
        Returns: (is_valid, error_message or None)
        """
        if not cedula:
            return False, "Cédula es requerida"
        
        if not re.match(r'^\d{10}$', cedula):
            return False, "Cédula debe tener 10 dígitos"
        
        return True, None

    @staticmethod
    def validate_positive_number(value, field_name="valor"):
        """
        Validate that value is a positive number
        Returns: (is_valid, error_message or None)
        """
        try:
            num = float(value)
            if num <= 0:
                return False, f"{field_name} debe ser mayor a 0"
            return True, None
        except (ValueError, TypeError):
            return False, f"{field_name} debe ser un número válido"

    @staticmethod
    def validate_positive_integer(value, field_name="valor"):
        """
        Validate that value is a positive integer
        Returns: (is_valid, error_message or None)
        """
        try:
            num = int(value)
            if num <= 0:
                return False, f"{field_name} debe ser mayor a 0"
            return True, None
        except (ValueError, TypeError):
            return False, f"{field_name} debe ser un número entero válido"

    @staticmethod
    def validate_product_data(data):
        """
        Validate product creation/update data
        Returns: (is_valid, error_message or None)
        """
        required = ['nombre', 'precio', 'stock', 'mililitros', 'categoria_id']
        is_valid, missing = Validator.validate_required_fields(data, required)
        if not is_valid:
            return False, f"Faltan campos: {', '.join(missing)}"

        # Validate precio
        is_valid, error = Validator.validate_positive_number(data['precio'], 'Precio')
        if not is_valid:
            return False, error

        # Validate stock
        is_valid, error = Validator.validate_positive_integer(data['stock'], 'Stock')
        if not is_valid:
            return False, error

        # Validate mililitros
        is_valid, error = Validator.validate_positive_integer(data['mililitros'], 'Mililitros')
        if not is_valid:
            return False, error

        return True, None
