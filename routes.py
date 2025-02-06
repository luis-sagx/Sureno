from flask import Blueprint, request, jsonify
from models import Producto
from bson import ObjectId
from bson.errors import InvalidId

productos_bp = Blueprint('productos', __name__)

@productos_bp.route('/productos', methods=['GET'])
def obtener_productos():
    productos = Producto.obtener_todos()
    return jsonify([{
        'id': str(p.id),
        'nombre': p.nombre,
        'precio': p.precio,
        'descripcion': p.descripcion,
        'stock': p.stock,
        'mililitros': p.mililitros
    } for p in productos])

@productos_bp.route('/productos', methods=['POST'])
def crear_producto():
    datos = request.get_json()
    try:
        producto = Producto(
            nombre=datos['nombre'],
            precio=float(datos['precio']),
            descripcion=datos['descripcion'],
            stock=int(datos['stock']),
            mililitros=int(datos['mililitros'])
        )
        producto.guardar()
        return jsonify({
            'mensaje': 'Producto creado exitosamente',
            'id': str(producto.id)
        }), 201
    except KeyError as e:
        return jsonify({'error': f'Falta el campo {str(e)}'}), 400
    except ValueError:
        return jsonify({'error': 'Valores inválidos'}), 400

@productos_bp.route('/productos/<id>', methods=['GET'])
def obtener_producto(id):
    try:
        producto = Producto.obtener_por_id(id)
        if producto:
            return jsonify({
                'id': str(producto.id),
                'nombre': producto.nombre,
                'precio': producto.precio,
                'descripcion': producto.descripcion,
                'stock': producto.stock,
                'mililitros': producto.mililitros
            })
        return jsonify({'error': 'Producto no encontrado'}), 404
    except InvalidId:
        return jsonify({'error': 'ID inválido'}), 400

@productos_bp.route('/productos/<id>', methods=['PUT'])
def actualizar_producto(id):
    try:
        producto = Producto.obtener_por_id(id)
        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404

        datos = request.get_json()
        producto.nombre = datos.get('nombre', producto.nombre)
        producto.precio = float(datos.get('precio', producto.precio))
        producto.descripcion = datos.get('descripcion', producto.descripcion)
        producto.stock = int(datos.get('stock', producto.stock))
        producto.mililitros = int(datos.get('mililitros', producto.mililitros))
        
        producto.guardar()
        return jsonify({'mensaje': 'Producto actualizado exitosamente'})
    except ValueError:
        return jsonify({'error': 'Valores inválidos'}), 400

@productos_bp.route('/productos/<id>', methods=['DELETE'])
def eliminar_producto(id):
    try:
        producto = Producto.obtener_por_id(id)
        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        producto.eliminar()
        return jsonify({'mensaje': 'Producto eliminado exitosamente'})
    except InvalidId:
        return jsonify({'error': 'ID inválido'}), 400

@productos_bp.route('/productos/buscar/<nombre>', methods=['GET'])
def buscar_productos(nombre):
    productos = Producto.buscar_por_nombre(nombre)
    return jsonify([{
        'id': str(p.id),
        'nombre': p.nombre,
        'precio': p.precio,
        'descripcion': p.descripcion,
        'stock': p.stock,
        'mililitros': p.mililitros
    } for p in productos])