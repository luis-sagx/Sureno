from flask import Blueprint, request, jsonify, render_template
from models.product import ProductModel
from bson.objectid import ObjectId
import os
from werkzeug.utils import secure_filename
from config import db

product_routes = Blueprint('product_routes', __name__)

UPLOAD_FOLDER = "static/uploads"
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
    
@product_routes.route('/products')
def products():
    products = ProductModel.get_all()
    for product in products:
        product['_id'] = str(product['_id'])
    return render_template('product.html', products=products)

@product_routes.route('/products/<product_id>', methods=['GET'])
def product_detail(product_id):
    product = ProductModel.get_by_id(product_id)
    if product:
        return render_template('product_detail.html', product=product)
    else:
        return "Producto no encontrado", 404

@product_routes.route('/products', methods=['POST'])
def create_product():
    # Obtener datos del producto
    nombre = request.form.get('nombre')
    precio = float(request.form.get('precio'))
    stock = int(request.form.get('stock'))
    mililitros = int(request.form.get('mililitros'))
    categoria_id = request.form.get('categoria_id')
    
    # Manejar la imagen
    imagen = request.files.get('imagen')
    image_path = ""
    
    if imagen and allowed_file(imagen.filename):
        filename = secure_filename(imagen.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        imagen.save(filepath)
        image_path = f"/static/uploads/{filename}"

    # Crear el producto
    product_data = {
        "nombre": nombre,
        "precio": precio,
        "stock": stock,
        "mililitros": mililitros,
        "categoria_id": categoria_id,
        "imagen": image_path
    }

    inserted_id = ProductModel.create(product_data)
    if inserted_id:
        return jsonify({'message': 'Producto creado', 'id': inserted_id}), 201
    return jsonify({'error': 'Error al crear el producto'}), 400

@product_routes.route('/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        # Obtener datos del formulario
        nombre = request.form.get('nombre')
        precio = float(request.form.get('precio'))
        stock = int(request.form.get('stock'))
        mililitros = int(request.form.get('mililitros'))
        categoria_id = request.form.get('categoria_id')
        
        # Preparar los datos de actualización
        update_data = {
            "nombre": nombre,
            "precio": precio,
            "stock": stock,
            "mililitros": mililitros,
            "categoria_id": categoria_id
        }

        # Manejar la imagen si se proporcionó una nueva
        if 'imagen' in request.files:
            imagen = request.files['imagen']
            if imagen and allowed_file(imagen.filename):
                filename = secure_filename(imagen.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                imagen.save(filepath)
                update_data['imagen'] = f"/static/uploads/{filename}"

        # Actualizar el producto
        modified_count = ProductModel.update(product_id, update_data)
        
        if modified_count:
            return jsonify({'message': 'Producto actualizado exitosamente'}), 200
        return jsonify({'error': 'Producto no encontrado o no hubo cambios'}), 404

    except Exception as e:
        print(f"Error al actualizar producto: {str(e)}")
        return jsonify({'error': 'Error al actualizar producto'}), 500

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
