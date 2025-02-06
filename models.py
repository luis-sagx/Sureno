from config import db
from bson.objectid import ObjectId

class Producto:
    collection = db.productos
    
    def __init__(self, nombre, precio, descripcion, stock, mililitros, _id=None):
        self.id = ObjectId(_id) if _id else None
        self.nombre = nombre
        self.precio = precio
        self.descripcion = descripcion
        self.stock = stock
        self.mililitros = mililitros

    def guardar(self):
        if not self.id:
            result = self.collection.insert_one(self.__dict__)
            self.id = result.inserted_id
        else:
            self.collection.update_one(
                {'_id': self.id},
                {'$set': {
                    'nombre': self.nombre,
                    'precio': self.precio,
                    'descripcion': self.descripcion,
                    'stock': self.stock,
                    'mililitros': self.mililitros
                }}
            )
        return self

    @classmethod
    def obtener_todos(cls):
        return [cls(**producto) for producto in cls.collection.find()]

    @classmethod
    def obtener_por_id(cls, id):
        producto = cls.collection.find_one({'_id': ObjectId(id)})
        return cls(**producto) if producto else None

    def eliminar(self):
        if self.id:
            self.collection.delete_one({'_id': self.id})
            return True
        return False

    @classmethod
    def buscar_por_nombre(cls, nombre):
        productos = cls.collection.find({'nombre': {'$regex': nombre, '$options': 'i'}})
        return [cls(**producto) for producto in productos]