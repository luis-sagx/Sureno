"""
File Handler - Utilities for file upload and management
"""
import os
from werkzeug.utils import secure_filename


class FileHandler:
    """Utility class for file handling"""
    
    UPLOAD_FOLDER = "static/uploads"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

    @staticmethod
    def allowed_file(filename):
        """
        Check if file extension is allowed
        """
        return "." in filename and \
               filename.rsplit(".", 1)[1].lower() in FileHandler.ALLOWED_EXTENSIONS

    @staticmethod
    def save_image(image_file):
        """
        Save uploaded image file
        Returns: (success, file_path or error_message)
        """
        if not image_file:
            return False, "No se envió ninguna imagen"

        if image_file.filename == "":
            return False, "Nombre de archivo vacío"

        if not FileHandler.allowed_file(image_file.filename):
            return False, f"Formato no permitido. Extensiones permitidas: {', '.join(FileHandler.ALLOWED_EXTENSIONS)}"

        try:
            # Ensure upload folder exists
            os.makedirs(FileHandler.UPLOAD_FOLDER, exist_ok=True)

            # Save file
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(FileHandler.UPLOAD_FOLDER, filename)
            image_file.save(filepath)

            # Return web path
            image_path = f"/static/uploads/{filename}"
            return True, image_path

        except Exception as e:
            return False, f"Error al guardar archivo: {str(e)}"

    @staticmethod
    def delete_image(image_path):
        """
        Delete image file
        Returns: (success, message or error_message)
        """
        try:
            if not image_path or image_path.startswith('/static/img/'):
                return True, "No hay archivo para eliminar"

            # Convert web path to file system path
            if image_path.startswith('/static/uploads/'):
                filename = image_path.split('/')[-1]
                filepath = os.path.join(FileHandler.UPLOAD_FOLDER, filename)
                
                if os.path.exists(filepath):
                    os.remove(filepath)
                    return True, "Archivo eliminado"

            return True, "Archivo no encontrado"

        except Exception as e:
            return False, f"Error al eliminar archivo: {str(e)}"

    @staticmethod
    def get_file_from_request(request, field_name='imagen'):
        """
        Extract file from request
        Returns: file object or None
        """
        if field_name not in request.files:
            return None
        
        file = request.files[field_name]
        if file.filename == '':
            return None
            
        return file
