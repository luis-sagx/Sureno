"""
Product Routes - API and web endpoints for product management
"""
from flask import Blueprint, request, jsonify, render_template
from services.product_service import ProductService
from utils.file_handler import FileHandler
from utils.response_handler import ResponseHandler
from utils.decorators import admin_required
from utils.validators import Validator


product_routes = Blueprint('product_routes', __name__)


@product_routes.route('/upload-image/<product_id>', methods=['POST'])
@admin_required
def upload_image(product_id):
    """Upload image for a product"""
    image_file = FileHandler.get_file_from_request(request, 'imagen')
    
    if not image_file:
        return ResponseHandler.bad_request("No se envió ninguna imagen")
    
    # Save image
    success, result = FileHandler.save_image(image_file)
    if not success:
        return ResponseHandler.bad_request(result)
    
    # Update product
    success, data, status_code = ProductService.update_product_image(product_id, result)
    
    if not success:
        return ResponseHandler.error(data, status_code)
    
    return jsonify(data), status_code


@product_routes.route('/products')
def products():
    """Show products page"""
    products = ProductService.get_all_products()
    return render_template('product.html', products=products)


@product_routes.route('/products/<product_id>', methods=['GET'])
def product_detail(product_id):
    """Show product detail page"""
    success, product, status_code = ProductService.get_product_by_id(product_id)
    
    if not success:
        return "Producto no encontrado", 404
    
    return render_template('product_detail.html', product=product)


@product_routes.route('/products', methods=['POST'])
@admin_required
def create_product():
    """Create a new product"""
    # Get form data
    product_data = {
        'nombre': request.form.get('nombre'),
        'precio': request.form.get('precio'),
        'stock': request.form.get('stock'),
        'mililitros': request.form.get('mililitros'),
        'categoria_id': request.form.get('categoria_id')
    }
    
    # Validate product data
    is_valid, error = Validator.validate_product_data(product_data)
    if not is_valid:
        return ResponseHandler.bad_request(error)
    
    # Convert numeric fields
    product_data['precio'] = float(product_data['precio'])
    product_data['stock'] = int(product_data['stock'])
    product_data['mililitros'] = int(product_data['mililitros'])
    
    # Handle image upload
    image_path = None
    image_file = FileHandler.get_file_from_request(request, 'imagen')
    if image_file:
        success, result = FileHandler.save_image(image_file)
        if success:
            image_path = result
        else:
            return ResponseHandler.bad_request(result)
    
    # Create product
    success, result, status_code = ProductService.create_product(product_data, image_path)
    
    if not success:
        return ResponseHandler.error(result, status_code)
    
    return ResponseHandler.created({'id': result}, 'Producto creado')


@product_routes.route('/products/<product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    """Update product"""
    try:
        # Get form data
        update_data = {
            'nombre': request.form.get('nombre'),
            'precio': float(request.form.get('precio')),
            'stock': int(request.form.get('stock')),
            'mililitros': int(request.form.get('mililitros')),
            'categoria_id': request.form.get('categoria_id')
        }
        
        # Validate
        is_valid, error = Validator.validate_product_data(update_data)
        if not is_valid:
            return ResponseHandler.bad_request(error)
        
        # Handle image upload if provided
        image_path = None
        image_file = FileHandler.get_file_from_request(request, 'imagen')
        if image_file:
            success, result = FileHandler.save_image(image_file)
            if success:
                image_path = result
            else:
                return ResponseHandler.bad_request(result)
        
        # Update product
        success, result, status_code = ProductService.update_product(
            product_id, 
            update_data, 
            image_path
        )
        
        if not success:
            return ResponseHandler.error(result, status_code)
        
        return ResponseHandler.success(message=result)
        
    except (ValueError, KeyError) as e:
        return ResponseHandler.bad_request(f"Datos inválidos: {str(e)}")


@product_routes.route('/products/<product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """Delete product"""
    success, result, status_code = ProductService.delete_product(product_id)
    
    if not success:
        return ResponseHandler.error(result, status_code)
    
    return ResponseHandler.success(message=result)

