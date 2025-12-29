"""
Main Application File
"""
from flask import Flask, render_template, session
from routes import register_routes
from constants import config
import os


def create_app(config_name='default'):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    app.secret_key = app.config['SECRET_KEY']
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    register_routes(app)
    
    # Register general routes
    @app.route('/')
    def confirmacion():
        return render_template('confirmacion.html')
    
    @app.route('/index')
    def index():
        return render_template('index.html')
    
    @app.route('/about')
    def about():
        return render_template('aboutUs.html')
    
    @app.route('/contact')
    def contact():
        return render_template('contact.html')
    
    @app.route('/cart')
    def cart():
        return render_template('cart.html')
    
    @app.route('/checkOut')
    def checkOut():
        return render_template('checkOut.html')
    
    @app.route('/login')
    def login():
        return render_template('login.html')
    
    @app.route('/signUp')
    def signUp():
        return render_template('signUp.html')
    
    return app


# Create app instance
app = create_app(os.environ.get('FLASK_ENV', 'default'))


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], use_reloader=False)

