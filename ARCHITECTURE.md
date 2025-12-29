# Arquitectura del Proyecto Sureño

## 📁 Estructura del Proyecto

```
Sureno/
├── app.py                 # Punto de entrada de la aplicación
├── config.py              # Configuración de base de datos
├── constants.py           # Constantes y configuraciones
├── requirements.txt       # Dependencias del proyecto
│
├── models/                # 📦 Capa de Datos (Data Layer)
│   ├── __init__.py
│   ├── user.py           # Modelo de Usuario
│   ├── product.py        # Modelo de Producto
│   ├── cart.py           # Modelo de Carrito
│   ├── order.py          # Modelo de Pedido
│   ├── address.py        # Modelo de Dirección
│   └── category.py       # Modelo de Categoría
│
├── services/              # 🔧 Capa de Negocio (Business Logic Layer)
│   ├── __init__.py
│   ├── auth_service.py   # Lógica de autenticación
│   ├── user_service.py   # Lógica de usuarios
│   ├── product_service.py # Lógica de productos
│   ├── cart_service.py   # Lógica de carrito
│   └── order_service.py  # Lógica de pedidos
│
├── routes/                # 🌐 Capa de Presentación (Presentation Layer)
│   ├── __init__.py
│   ├── auth_routes.py    # Rutas de autenticación
│   ├── user_routes.py    # Rutas de usuarios
│   ├── product_routes.py # Rutas de productos
│   ├── cart_routes.py    # Rutas de carrito
│   ├── order_routes.py   # Rutas de pedidos
│   ├── address_routes.py # Rutas de direcciones
│   └── admin_routes.py   # Rutas de administración
│
├── utils/                 # 🛠️ Utilidades (Utilities)
│   ├── __init__.py
│   ├── decorators.py     # Decoradores (auth, admin)
│   ├── validators.py     # Validadores de datos
│   ├── file_handler.py   # Manejo de archivos
│   └── response_handler.py # Respuestas estandarizadas
│
├── static/                # 📂 Archivos estáticos
│   ├── css/
│   ├── js/
│   ├── img/
│   └── uploads/
│
└── templates/             # 📄 Plantillas HTML
    ├── base.html
    ├── index.html
    ├── login.html
    ├── admin/
    └── partials/
```

## 🏗️ Arquitectura en Capas

### 1. **Capa de Presentación (Routes)**

- **Responsabilidad**: Manejar peticiones HTTP y respuestas
- **Características**:
  - Blueprints de Flask organizados por dominio
  - Uso de decoradores para autenticación y autorización
  - Validación de entrada con helpers
  - Respuestas estandarizadas

**Ejemplo:**

```python
@product_routes.route('/products', methods=['POST'])
@admin_required
def create_product():
    # Validación
    is_valid, error = Validator.validate_product_data(data)

    # Delegar a servicio
    success, result, code = ProductService.create_product(data)

    # Respuesta estandarizada
    return ResponseHandler.created({'id': result})
```

### 2. **Capa de Negocio (Services)**

- **Responsabilidad**: Lógica de negocio y reglas de la aplicación
- **Características**:
  - Encapsula la lógica de negocio
  - Coordina entre modelos
  - Validaciones de negocio
  - Retorna tuplas `(success, data/error, status_code)`

**Ejemplo:**

```python
class ProductService:
    @staticmethod
    def create_product(product_data, image_path=None):
        try:
            if image_path:
                product_data['imagen'] = image_path

            inserted_id = ProductModel.create(product_data)
            return True, inserted_id, 201
        except Exception as e:
            return False, str(e), 500
```

### 3. **Capa de Datos (Models)**

- **Responsabilidad**: Acceso a datos y operaciones CRUD
- **Características**:
  - Interacción directa con MongoDB
  - Métodos estáticos para operaciones CRUD
  - Transformación de datos (ObjectId ↔ string)
  - Sin lógica de negocio

**Ejemplo:**

```python
class ProductModel:
    @staticmethod
    def create(product_data):
        result = db.productos.insert_one(product_data)
        return str(result.inserted_id)

    @staticmethod
    def get_by_id(product_id):
        return db.productos.find_one({"_id": ObjectId(product_id)})
```

### 4. **Utilidades (Utils)**

- **Decoradores**: `@login_required`, `@admin_required`
- **Validadores**: Validación de emails, passwords, datos
- **Manejadores**: Archivos, respuestas HTTP
- **Helpers**: Funciones reutilizables

## 🔐 Flujo de Autenticación

```
1. Usuario → POST /api/auth/login
2. auth_routes → AuthService.authenticate_user()
3. AuthService → UserModel.get_by_email() → MongoDB
4. AuthService ← Valida contraseña con bcrypt
5. AuthService ← Crea datos de sesión
6. auth_routes ← Establece session
7. Usuario ← JSON con redirect URL
```

## 🛡️ Principios de Diseño Aplicados

### SOLID Principles

1. **Single Responsibility (SRP)**

   - Cada clase/módulo tiene una única responsabilidad
   - Services: lógica de negocio
   - Models: acceso a datos
   - Routes: manejo de HTTP

2. **Open/Closed (OCP)**

   - ResponseHandler permite extensión sin modificación
   - Decoradores añaden funcionalidad sin cambiar rutas

3. **Liskov Substitution (LSP)**

   - Todos los servicios siguen el mismo patrón de respuesta
   - `(success, data/error, status_code)`

4. **Interface Segregation (ISP)**

   - Servicios específicos por dominio
   - No hay interfaces gordas

5. **Dependency Inversion (DIP)**
   - Routes dependen de Services (abstracción)
   - Services dependen de Models (abstracción)
   - No hay dependencia directa a MongoDB en routes

### Separation of Concerns

- **Presentación**: Routes
- **Negocio**: Services
- **Datos**: Models
- **Transversal**: Utils

### DRY (Don't Repeat Yourself)

- Validaciones centralizadas en `Validators`
- Manejo de archivos en `FileHandler`
- Respuestas en `ResponseHandler`
- Autenticación en decoradores

## 📝 Patrones de Uso

### Crear una nueva ruta

```python
from flask import Blueprint, request
from services.my_service import MyService
from utils.decorators import login_required
from utils.response_handler import ResponseHandler

my_routes = Blueprint('my_routes', __name__)

@my_routes.route('/resource', methods=['POST'])
@login_required
def create_resource():
    data = request.get_json()

    success, result, code = MyService.create(data)

    if not success:
        return ResponseHandler.error(result, code)

    return ResponseHandler.created({'id': result})
```

### Crear un nuevo servicio

```python
from models.my_model import MyModel

class MyService:
    @staticmethod
    def create(data):
        try:
            # Validaciones de negocio
            if not data.get('required_field'):
                return False, "Campo requerido", 400

            # Operación
            inserted_id = MyModel.create(data)
            return True, inserted_id, 201

        except Exception as e:
            return False, str(e), 500
```

## 🔧 Configuración

### Variables de Entorno

```bash
# .env
SECRET_KEY=your-secret-key-here
DEBUG=True
MONGO_URI=mongodb+srv://...
DATABASE_NAME=Sureno
FLASK_ENV=development
```

### Constantes

Definidas en `constants.py`:

- `Config.SECRET_KEY`
- `Config.UPLOAD_FOLDER`
- `Config.MAX_CONTENT_LENGTH`
- `Config.ROLE_CLIENTE = 1`
- `Config.ROLE_ADMIN = 2`
- `Config.SHIPPING_COST = 3.0`

## 🚀 Ejecución

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python app.py

# O con variables de entorno
FLASK_ENV=production python app.py
```

## 📊 Ventajas de esta Arquitectura

1. **Mantenibilidad**: Código organizado y fácil de encontrar
2. **Escalabilidad**: Fácil añadir nuevas funcionalidades
3. **Testabilidad**: Capas independientes son fáciles de probar
4. **Reutilización**: Servicios y utils son reutilizables
5. **Legibilidad**: Código limpio y bien documentado
6. **Seguridad**: Autenticación y autorización centralizadas
7. **Consistencia**: Patrones estandarizados en toda la app

## 🔄 Flujo de una Petición Típica

```
1. Cliente HTTP
   ↓
2. Route (Blueprint)
   ↓
3. Decorator (@login_required)
   ↓
4. Validator (validación de datos)
   ↓
5. Service (lógica de negocio)
   ↓
6. Model (acceso a BD)
   ↓
7. MongoDB
   ↓
8. Model (transformación)
   ↓
9. Service (procesamiento)
   ↓
10. ResponseHandler (formato de respuesta)
    ↓
11. Route (return)
    ↓
12. Cliente HTTP
```

## 📚 Siguientes Pasos Recomendados

1. Implementar tests unitarios para servicios
2. Añadir logging centralizado
3. Implementar caché (Redis)
4. Añadir migraciones de BD
5. Documentar API con Swagger/OpenAPI
6. Implementar rate limiting
7. Añadir monitoring y métricas
