"""
Application Constants
"""
import os


class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'supersecreto')
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
    
    # File Upload
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Database
    MONGO_URI = os.environ.get('MONGO_URI')
    DATABASE_NAME = os.environ.get('DATABASE_NAME', 'Sureno')
    
    if not MONGO_URI:
        raise ValueError(
            "MONGO_URI no está configurado. Por favor, crea un archivo .env "
            "en la raíz del proyecto con tu URI de MongoDB Atlas.\n"
            "Ejemplo: MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/"
        )
    
    # Roles
    ROLE_CLIENTE = 1
    ROLE_ADMIN = 2
    
    # Order
    SHIPPING_COST = 3.0


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # In production, SECRET_KEY should always come from environment
    SECRET_KEY = os.environ.get('SECRET_KEY')


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
