from flask import Blueprint, request, jsonify, render_template
from config import db
from models.category import CategoryModel 
from models.product import ProductModel 
from models.order import OrderModel 

admin_routes = Blueprint('admin_routes', __name__)

@admin_routes.route('/home')
def admin_home():
    total_clientes = db.usuarios.count_documents({})
    total_productos = db.productos.count_documents({})
    total_pedidos = db.orders.count_documents({})
    return render_template('admin/home.html', total_clientes=total_clientes, total_productos=total_productos, total_pedidos=total_pedidos)

@admin_routes.route('/orders')
def admin_orders():
    pedidos = OrderModel.get_all()
    return render_template('admin/orders.html', pedidos=pedidos)

@admin_routes.route('/products')
def admin_product_list():
    productos = ProductModel.get_all()  # Usar el modelo en lugar de acceder directamente a la BD
    categorias = CategoryModel.get_all()
    return render_template('admin/admin_products.html', 
                         productos=productos, 
                         categorias=categorias)