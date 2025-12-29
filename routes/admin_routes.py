"""
Admin Routes - Admin panel pages
"""
from flask import Blueprint, render_template
from config import db
from models.category import CategoryModel 
from models.product import ProductModel 
from models.order import OrderModel
from utils.decorators import admin_required


admin_routes = Blueprint('admin_routes', __name__)


@admin_routes.route('/home')
@admin_required
def admin_home():
    """Admin dashboard home"""
    total_clientes = db.usuarios.count_documents({})
    total_productos = db.productos.count_documents({})
    total_pedidos = db.orders.count_documents({})
    
    return render_template(
        'admin/home.html', 
        total_clientes=total_clientes, 
        total_productos=total_productos, 
        total_pedidos=total_pedidos
    )


@admin_routes.route('/orders')
@admin_required
def admin_orders():
    """Admin orders page"""
    pedidos = OrderModel.get_all()
    return render_template('admin/orders.html', pedidos=pedidos)


@admin_routes.route('/products')
@admin_required
def admin_product_list():
    """Admin products management page"""
    productos = ProductModel.get_all()
    categorias = CategoryModel.get_all()
    
    return render_template(
        'admin/admin_products.html', 
        productos=productos, 
        categorias=categorias
    )
