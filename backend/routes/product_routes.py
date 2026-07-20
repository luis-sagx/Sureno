from flask import Blueprint, request, jsonify
from models.product import ProductModel
from models.category import CategoryModel
from bson.objectid import ObjectId
import os
from werkzeug.utils import secure_filename
from config import db
from routes.auth import admin_required_api

product_routes = Blueprint('product_routes', __name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _save_image(image):
    """Guarda una imagen válida y devuelve su ruta pública."""
    if not image or not allowed_file(image.filename):
        return None
    filename = secure_filename(image.filename)
    image.save(os.path.join(UPLOAD_FOLDER, filename))
    return f"/static/uploads/{filename}"


def _product_form_data():
    """Convierte el formulario común de creación/edición a tipos de dominio."""
    return {
        "nombre": request.form.get('nombre'),
        "precio": float(request.form.get('precio')),
        "stock": int(request.form.get('stock')),
        "mililitros": int(request.form.get('mililitros')),
        "categoria_id": request.form.get('categoria_id'),
    }

@product_routes.route('/upload-image/<product_id>', methods=['POST'])
@admin_required_api
def upload_image(product_id):
    if "imagen" not in request.files:
        return jsonify({"error": "No se envió ninguna imagen"}), 400
    
    imagen = request.files["imagen"]
    if imagen.filename == "" or not allowed_file(imagen.filename):
        return jsonify({"error": "Formato no permitido"}), 400
    
    image_path = _save_image(imagen)
    updated = ProductModel.update_image(product_id, image_path)

    if updated:
        return jsonify({"mensaje": "Imagen subida con éxito", "ruta": image_path}), 200
    else:
        return jsonify({"error": "Producto no encontrado"}), 404
    
@product_routes.route('/products', methods=['GET'])
def products():
    """Lista de productos en JSON (consumida por el frontend Astro)."""
    productos = ProductModel.get_all()
    for producto in productos:
        producto['_id'] = str(producto['_id'])
        if producto.get('categoria_id') is not None:
            producto['categoria_id'] = str(producto['categoria_id'])
    return jsonify(productos), 200

@product_routes.route('/products/<product_id>', methods=['GET'])
def product_detail(product_id):
    """Detalle de un producto en JSON."""
    producto = ProductModel.get_by_id(product_id)  # ya devuelve _id/categoria_id como str
    if producto:
        return jsonify(producto), 200
    return jsonify({'error': 'Producto no encontrado'}), 404

@product_routes.route('/categories', methods=['GET'])
def categories():
    """Lista de categorías en JSON (para el formulario de productos del admin)."""
    categorias = CategoryModel.get_all()
    for categoria in categorias:
        categoria['_id'] = str(categoria['_id'])
    return jsonify(categorias), 200

@product_routes.route('/products', methods=['POST'])
@admin_required_api
def create_product():
    product_data = _product_form_data()
    product_data["imagen"] = _save_image(request.files.get('imagen')) or ""

    inserted_id = ProductModel.create(product_data)
    if inserted_id:
        return jsonify({'message': 'Producto creado', 'id': inserted_id}), 201
    return jsonify({'error': 'Error al crear el producto'}), 400

@product_routes.route('/products/<product_id>', methods=['PUT'])
@admin_required_api
def update_product(product_id):
    try:
        update_data = _product_form_data()
        image_path = _save_image(request.files.get('imagen'))
        if image_path:
            update_data['imagen'] = image_path

        # Actualizar el producto
        modified_count = ProductModel.update(product_id, update_data)
        
        if modified_count:
            return jsonify({'message': 'Producto actualizado exitosamente'}), 200
        return jsonify({'error': 'Producto no encontrado o no hubo cambios'}), 404

    except Exception as e:
        print(f"Error al actualizar producto: {str(e)}")
        return jsonify({'error': 'Error al actualizar producto'}), 500

@product_routes.route('/products/<product_id>', methods=['DELETE'])
@admin_required_api
def delete_product(product_id):
    """
    Elimina un producto existente.
    """
    deleted_count = ProductModel.delete(product_id) 
    if deleted_count:
        return jsonify({'message': 'Producto eliminado'}), 200
    else:
        return jsonify({'error': 'Producto no encontrado'}), 404
