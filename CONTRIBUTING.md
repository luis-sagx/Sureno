# Guía de Contribución - Proyecto Sureño

## Bienvenido

Gracias por tu interés en contribuir al proyecto Sureño. Esta guía te ayudará a entender cómo trabajar con el código y mantener la calidad del proyecto.

## Tabla de Contenidos

1. [Configuración del Entorno](#configuración-del-entorno)
2. [Arquitectura del Proyecto](#arquitectura-del-proyecto)
3. [Estándares de Código](#estándares-de-código)
4. [Flujo de Trabajo Git](#flujo-de-trabajo-git)
5. [Testing](#testing)
6. [Pull Requests](#pull-requests)

## Configuración del Entorno

### Requisitos Previos

- Python 3.10+
- MongoDB Atlas account
- Git
- Editor de código (VS Code recomendado)

### Setup Local

1. **Clonar el repositorio**:

   ```bash
   git clone https://github.com/luis-sagx/Sureno.git
   cd Sureno
   ```

2. **Crear entorno virtual**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**:

   ```bash
   cp .env.example .env
   # Edita .env con tus credenciales
   ```

5. **Ejecutar la aplicación**:
   ```bash
   python app.py
   ```

## Arquitectura del Proyecto

Antes de contribuir, familiarízate con la arquitectura:

- Lee [ARCHITECTURE.md](ARCHITECTURE.md) para backend
- Lee [FRONTEND_ARCHITECTURE.md](FRONTEND_ARCHITECTURE.md) para frontend
- Lee [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) para contexto histórico

### Principios Clave

1. **Separación de Responsabilidades**: Routes → Services → Models
2. **DRY (Don't Repeat Yourself)**: Reutiliza código existente
3. **SOLID Principles**: Escribe código mantenible
4. **Modularidad**: Mantén módulos independientes y enfocados

## Estándares de Código

### Python (Backend)

#### Convenciones de Nomenclatura

```python
# Clases: PascalCase
class UserService:
    pass

# Funciones y variables: snake_case
def get_user_by_id(user_id):
    user_name = "John"
    return user_name

# Constantes: UPPER_SNAKE_CASE
MAX_FILE_SIZE = 5242880
```

#### Estructura de Archivos

**Servicios** (`services/`):

```python
"""
Module docstring describing the service
"""

from typing import Tuple, Any
from models.user import User

class UserService:
    """Service for user-related business logic"""

    @staticmethod
    def get_user_by_id(user_id: str) -> Tuple[bool, Any, int]:
        """
        Get user by ID

        Args:
            user_id: The user ID

        Returns:
            Tuple of (success, data/error, status_code)
        """
        try:
            user = User.get_by_id(user_id)
            if not user:
                return False, "User not found", 404
            return True, user, 200
        except Exception as e:
            return False, str(e), 500
```

**Rutas** (`routes/`):

```python
"""
Module docstring describing the routes
"""

from flask import Blueprint, jsonify, request
from utils.decorators import login_required
from utils.response_handler import ResponseHandler
from services.user_service import UserService

user_bp = Blueprint('user', __name__)

@user_bp.route('/api/users/<user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """Get user by ID"""
    success, result, status = UserService.get_user_by_id(user_id)

    if success:
        return ResponseHandler.success(result)
    return ResponseHandler.error(result, status)
```

#### Imports

Ordena los imports en este orden:

```python
# 1. Standard library
import os
from datetime import datetime

# 2. Third-party packages
from flask import Flask, request
from pymongo import MongoClient

# 3. Local modules
from models.user import User
from services.auth_service import AuthService
from utils.validators import Validator
```

### JavaScript (Frontend)

#### Convenciones de Nomenclatura

```javascript
// Clases: PascalCase
class CartManager {
  constructor() {}
}

// Funciones y variables: camelCase
function getUserData() {
  const userName = "John";
  return userName;
}

// Constantes: UPPER_SNAKE_CASE
const MAX_CART_ITEMS = 50;
```

#### Estructura de Módulos

```javascript
/**
 * Module Name - Description
 *
 * @module moduleName
 */

class ModuleName {
  /**
   * Method description
   *
   * @param {string} param - Parameter description
   * @returns {Object} Return value description
   */
  static methodName(param) {
    // Implementation
  }
}

// Initialize on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  ModuleName.init();
});

// Export for Node.js (if needed)
if (typeof module !== "undefined" && module.exports) {
  module.exports = ModuleName;
}
```

### CSS

#### Nomenclatura

```css
/* Usa BEM para componentes específicos */
.product-card {
}
.product-card__image {
}
.product-card__title {
}
.product-card--featured {
}

/* Usa variables CSS para valores reutilizables */
.custom-button {
  background-color: var(--color-primary);
  padding: var(--spacing-3);
  border-radius: var(--radius-md);
}
```

#### Orden de Propiedades

```css
.element {
  /* 1. Positioning */
  position: relative;
  top: 0;
  left: 0;
  z-index: 10;

  /* 2. Box Model */
  display: flex;
  width: 100%;
  height: auto;
  margin: 0;
  padding: 1rem;

  /* 3. Typography */
  font-size: 1rem;
  line-height: 1.5;
  color: var(--color-text);

  /* 4. Visual */
  background-color: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);

  /* 5. Animation */
  transition: all 0.3s ease;
}
```

## Flujo de Trabajo Git

### Branching Strategy

```
main (producción)
  └── develop (desarrollo)
       ├── feature/nombre-feature
       ├── bugfix/nombre-bug
       └── hotfix/nombre-hotfix
```

### Crear una Nueva Feature

```bash
# 1. Asegúrate de estar actualizado
git checkout develop
git pull origin develop

# 2. Crea una nueva rama
git checkout -b feature/nombre-descriptivo

# 3. Realiza tus cambios y commits
git add .
git commit -m "feat: descripción clara del cambio"

# 4. Push a tu rama
git push origin feature/nombre-descriptivo

# 5. Crea un Pull Request en GitHub
```

### Convenciones de Commits

Usa [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: agregar validación de email en registro
fix: corregir cálculo de total en carrito
docs: actualizar README con instrucciones de instalación
style: formatear código en user_service.py
refactor: extraer lógica de autenticación a servicio
test: agregar tests para ProductService
chore: actualizar dependencias
```

### Ejemplos de Buenos Commits

```bash
# ✅ Buenos commits
git commit -m "feat: agregar endpoint para eliminar productos"
git commit -m "fix: corregir error en cálculo de envío"
git commit -m "refactor: mover validación a Validator class"

# ❌ Malos commits
git commit -m "cambios"
git commit -m "fix bug"
git commit -m "update"
```

## Testing

### Estructura de Tests (Por Implementar)

```
tests/
├── unit/
│   ├── test_services/
│   │   ├── test_user_service.py
│   │   └── test_product_service.py
│   └── test_utils/
│       ├── test_validators.py
│       └── test_file_handler.py
├── integration/
│   └── test_routes/
│       ├── test_user_routes.py
│       └── test_product_routes.py
└── e2e/
    └── test_user_flow.py
```

### Escribir Tests Unitarios

```python
import unittest
from services.user_service import UserService

class TestUserService(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures"""
        self.user_id = "test_user_123"

    def test_get_user_by_id_success(self):
        """Test successful user retrieval"""
        success, user, status = UserService.get_user_by_id(self.user_id)

        self.assertTrue(success)
        self.assertEqual(status, 200)
        self.assertIsNotNone(user)

    def test_get_user_by_id_not_found(self):
        """Test user not found"""
        success, error, status = UserService.get_user_by_id("invalid_id")

        self.assertFalse(success)
        self.assertEqual(status, 404)
```

### Ejecutar Tests

```bash
# Ejecutar todos los tests
python -m pytest tests/

# Ejecutar con coverage
python -m pytest --cov=. tests/

# Ejecutar tests específicos
python -m pytest tests/unit/test_services/test_user_service.py
```

## Pull Requests

### Checklist Antes de Crear PR

- [ ] El código sigue los estándares del proyecto
- [ ] Todos los tests pasan (cuando estén implementados)
- [ ] La documentación está actualizada
- [ ] Los commits siguen Conventional Commits
- [ ] No hay conflictos con la rama base
- [ ] El código está formateado correctamente

### Template de Pull Request

```markdown
## Descripción

Breve descripción de los cambios realizados.

## Tipo de Cambio

- [ ] Bug fix
- [ ] Nueva feature
- [ ] Breaking change
- [ ] Documentación

## ¿Cómo se ha probado?

Describe las pruebas realizadas.

## Checklist

- [ ] Mi código sigue los estándares del proyecto
- [ ] He actualizado la documentación
- [ ] He agregado tests (si aplica)
- [ ] Todos los tests pasan

## Screenshots (si aplica)

Agrega screenshots para cambios visuales.
```

## Áreas de Contribución

### Frontend

- Mejorar UI/UX de páginas existentes
- Agregar animaciones y transiciones
- Optimizar performance (lazy loading, code splitting)
- Mejorar accesibilidad (a11y)
- Implementar PWA features

### Backend

- Agregar tests unitarios e integración
- Implementar caching (Redis)
- Agregar logging estructurado
- Implementar rate limiting
- Mejorar seguridad (CSRF, XSS protection)

### DevOps

- Configurar CI/CD pipeline
- Agregar Docker support
- Implementar monitoreo (Sentry, etc.)
- Configurar backups automáticos
- Optimizar deployment process

### Documentación

- Mejorar documentación existente
- Agregar ejemplos de código
- Crear tutoriales
- Documentar API con Swagger/OpenAPI
- Traducir documentación

## Recursos Útiles

### Documentación

- [Flask Documentation](https://flask.palletsprojects.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/)
- [MDN Web Docs](https://developer.mozilla.org/)

### Herramientas

- [Python PEP 8 Style Guide](https://pep8.org/)
- [JavaScript Standard Style](https://standardjs.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)

### Comunicación

- Issues: Para reportar bugs o proponer features
- Discussions: Para preguntas y discusiones generales
- Pull Requests: Para contribuir código

## Preguntas Frecuentes

### ¿Cómo reporto un bug?

1. Verifica que el bug no esté ya reportado
2. Crea un nuevo issue con:
   - Descripción clara del problema
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Screenshots si es visual
   - Información del entorno (OS, navegador, etc.)

### ¿Cómo propongo una nueva feature?

1. Abre un issue con el tag "enhancement"
2. Describe:
   - El problema que resuelve
   - La solución propuesta
   - Alternativas consideradas
   - Impacto en el proyecto

### ¿Necesito permiso para trabajar en un issue?

No, pero es buena práctica comentar en el issue que vas a trabajar en él para evitar trabajo duplicado.

### ¿Cuánto tiempo toma revisar un PR?

Generalmente 2-3 días. Si es urgente, menciona en el PR.

## Código de Conducta

- Sé respetuoso con otros contribuidores
- Acepta críticas constructivas
- Enfócate en lo mejor para el proyecto
- Mantén discusiones profesionales

## Contacto

Para preguntas o ayuda:

- Email: info@sureno.com
- Issues: https://github.com/luis-sagx/Sureno/issues

---

¡Gracias por contribuir a Sureño! 🎉
