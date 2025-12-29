"""
Product Service - Handles product business logic
"""
from models.product import ProductModel


class ProductService:
    @staticmethod
    def get_all_products():
        """Get all products"""
        products = ProductModel.get_all()
        for product in products:
            product['_id'] = str(product['_id'])
        return products

    @staticmethod
    def get_product_by_id(product_id):
        """
        Get product by ID
        Returns: (success, product_data or error_message, status_code)
        """
        try:
            product = ProductModel.get_by_id(product_id)
            if product:
                return True, product, 200
            return False, "Producto no encontrado", 404
        except Exception as e:
            return False, str(e), 500

    @staticmethod
    def create_product(product_data, image_path=None):
        """
        Create a new product
        Returns: (success, inserted_id or error_message, status_code)
        """
        try:
            if image_path:
                product_data['imagen'] = image_path

            inserted_id = ProductModel.create(product_data)
            if inserted_id:
                return True, inserted_id, 201
            return False, "Error al crear el producto", 400
        except Exception as e:
            return False, str(e), 500

    @staticmethod
    def update_product(product_id, update_data, image_path=None):
        """
        Update product information
        Returns: (success, message or error_message, status_code)
        """
        try:
            if image_path:
                update_data['imagen'] = image_path

            modified_count = ProductModel.update(product_id, update_data)
            if modified_count:
                return True, "Producto actualizado exitosamente", 200
            return False, "Producto no encontrado o no hubo cambios", 404
        except Exception as e:
            return False, str(e), 500

    @staticmethod
    def delete_product(product_id):
        """
        Delete product
        Returns: (success, message or error_message, status_code)
        """
        try:
            deleted_count = ProductModel.delete(product_id)
            if deleted_count:
                return True, "Producto eliminado", 200
            return False, "Producto no encontrado", 404
        except Exception as e:
            return False, str(e), 500

    @staticmethod
    def update_product_image(product_id, image_path):
        """
        Update only product image
        Returns: (success, data or error_message, status_code)
        """
        try:
            updated = ProductModel.update_image(product_id, image_path)
            if updated:
                return True, {"mensaje": "Imagen subida con éxito", "ruta": image_path}, 200
            return False, "Producto no encontrado", 404
        except Exception as e:
            return False, str(e), 500
