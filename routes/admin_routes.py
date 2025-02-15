from flask import Blueprint, request, jsonify, render_template
from config import db

admin_routes = Blueprint('admin_routes', __name__)

@admin_routes.route('/home')
def admin_home():
    total_clientes = db.usuarios.count_documents({})
    total_productos = db.productos.count_documents({})
    total_pedidos = db.pedidos.count_documents({})
    return render_template('admin/home.html', total_clientes=total_clientes, total_productos=total_productos, total_pedidos=total_pedidos)

@admin_routes.route('/orders')
def admin_orders():
    pedidos = list(db.pedidos.find())
    return render_template('admin/orders.html', pedidos=pedidos)

@admin_routes.route('/products')
def admin_product_list():  # 🔹 Nombre cambiado para evitar conflicto
    productos = list(db.productos.find())
    for producto in productos:
        producto['_id'] = str(producto['_id'])  # Convertir ObjectId a string
    return render_template('admin/admin_products.html', productos=productos)
