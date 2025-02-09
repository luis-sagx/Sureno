from flask import Blueprint, request, jsonify, render_template
from models.product import ProductModel
from bson.objectid import ObjectId
import os
from werkzeug.utils import secure_filename

product_routes = Blueprint('product_routes', __name__)

# Configuración de carpeta de subida
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@product_routes.route('/upload-image/<product_id>', methods=['POST'])
def upload_image(product_id):
    if "imagen" not in request.files:
        return jsonify({"error": "No se envió ninguna imagen"}), 400
    
    imagen = request.files["imagen"]
    if imagen.filename == "" or not allowed_file(imagen.filename):
        return jsonify({"error": "Formato no permitido"}), 400
    
    filename = secure_filename(imagen.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    imagen.save(filepath)

    # Guardar la ruta en la base de datos
    image_path = f"/static/uploads/{filename}"
    updated = ProductModel.update_image(product_id, image_path)

    if updated:
        return jsonify({"mensaje": "Imagen subida con éxito", "ruta": image_path}), 200
    else:
        return jsonify({"error": "Producto no encontrado"}), 404


@product_routes.route('/api/products', methods=['GET'])
def get_products():
    products = ProductModel.get_all() 
    # Convierte el ObjectId a string para que JSON sea serializable
    for product in products:
        product['_id'] = str(product['_id'])
    return jsonify(products), 200

@product_routes.route('/products', methods=['GET'])
def show_products():
    products = ProductModel.get_all()
    # Convertir ObjectId a string para evitar problemas en la plantilla
    for product in products:
        product['_id'] = str(product['_id'])
    print("Productos obtenidos:", products)
    return render_template('product.html', products=products)

@product_routes.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """
    Devuelve un producto específico dado su id.
    """
    product = ProductModel.get_by_id(product_id)  # Usamos get_by_id()
    if product:
        product['_id'] = str(product['_id'])
        return jsonify(product), 200
    else:
        return jsonify({'error': 'Producto no encontrado'}), 404

@product_routes.route('/products', methods=['POST'])
def create_product():
    """
    Crea un nuevo producto.
    Se espera que la petición incluya un JSON con la información del producto.
    """
    data = request.get_json()
    inserted_id = ProductModel.create(data) 
    return jsonify({'message': 'Producto creado', 'id': inserted_id}), 201

@product_routes.route('/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    """
    Actualiza los datos de un producto existente.
    """
    update_data = request.get_json()
    modified_count = ProductModel.update(product_id, update_data)  
    if modified_count:
        return jsonify({'message': 'Producto actualizado'}), 200
    else:
        return jsonify({'error': 'Producto no encontrado o no hubo cambios'}), 404

@product_routes.route('/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """
    Elimina un producto existente.
    """
    deleted_count = ProductModel.delete(product_id) 
    if deleted_count:
        return jsonify({'message': 'Producto eliminado'}), 200
    else:
        return jsonify({'error': 'Producto no encontrado'}), 404
