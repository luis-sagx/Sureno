# Frontend Architecture

## Overview

El frontend de Sureño sigue una arquitectura modular organizada en capas separadas para estilos (CSS) y funcionalidad (JavaScript). Esta estructura promueve la reutilización de código, facilita el mantenimiento y mejora la consistencia visual de la aplicación.

## Estructura de Directorios

```
static/
├── css/
│   ├── _variables.css       # Variables CSS y tokens de diseño
│   ├── _base.css           # Reset CSS y estilos fundamentales
│   ├── _typography.css     # Sistema tipográfico
│   ├── _buttons.css        # Componentes de botones
│   ├── _forms.css          # Estilos de formularios
│   ├── _cards.css          # Componentes de tarjetas
│   ├── _navbar.css         # Navegación
│   ├── _layout.css         # Grid y layout utilities
│   ├── _utilities.css      # Clases utilitarias
│   ├── main.css            # Importa todos los módulos
│   ├── index.css           # Estilos específicos de página
│   ├── login.css           # Estilos de login
│   ├── cart.css            # Estilos de carrito
│   └── ...                 # Otros estilos por página
│
├── js/
│   ├── utils/
│   │   ├── api.js          # Comunicación con API
│   │   ├── storage.js      # Manejo de localStorage
│   │   ├── validation.js   # Validaciones
│   │   └── notify.js       # Notificaciones (SweetAlert2)
│   │
│   ├── modules/
│   │   ├── cart.js         # Funcionalidad del carrito
│   │   ├── auth.js         # Autenticación
│   │   └── products.js     # Productos
│   │
│   ├── main.js             # Inicialización general
│   ├── login.js            # Script de login
│   ├── admin.js            # Panel de administración
│   └── ...                 # Otros scripts por página
│
└── img/                    # Recursos de imagen
    └── uploads/            # Imágenes subidas

```

## Sistema CSS Modular

### 1. Variables CSS (\_variables.css)

Define todos los tokens de diseño del sistema:

**Colores:**

- `--color-primary`: Color principal (café)
- `--color-secondary`: Color secundario (beige)
- `--color-accent`: Color de acento (naranja)
- Variantes para estados (hover, active, etc.)
- Colores semánticos (success, warning, error, info)

**Tipografía:**

- `--font-primary`: Fuente principal
- `--font-heading`: Fuente para encabezados
- Escala tipográfica (xs, sm, base, lg, xl, 2xl, 3xl)
- Pesos de fuente (light, regular, medium, bold)

**Espaciado:**

- Escala de espaciado (1-12) basada en múltiplos de 0.25rem
- `--spacing-1` = 0.25rem (4px)
- `--spacing-12` = 3rem (48px)

**Bordes y Sombras:**

- Radios de borde (sm, md, lg, full)
- Sombras (sm, md, lg, xl)

**Tema Oscuro:**

- Todas las variables se redefinen en `body.dark-mode`
- Transiciones suaves entre temas

### 2. Base Styles (\_base.css)

- CSS Reset para consistencia cross-browser
- Box-sizing: border-box global
- Estilos por defecto para elementos HTML
- Smooth scrolling

### 3. Componentes Reutilizables

**Botones (\_buttons.css):**

```css
.btn                    /* Base button */
.btn-primary           /* Primary button */
.btn-secondary         /* Secondary button */
.btn-outline           /* Outline button */
.btn-ghost             /* Ghost button */
.btn-sm / .btn-lg      /* Size variants */
.btn:disabled          /* Disabled state */
```

**Formularios (\_forms.css):**

```css
.form-group            /* Form group wrapper */
/* Form group wrapper */
.form-label            /* Form label */
.form-control          /* Input field */
.is-invalid / .is-valid /* Validation states */
.form-check; /* Checkbox/radio wrapper */
```

**Tarjetas (\_cards.css):**

```css
.card                  /* Base card */
/* Base card */
.card-header           /* Card header */
.card-body             /* Card body */
.card-footer           /* Card footer */
.product-card; /* Specialized product card */
```

**Navegación (\_navbar.css):**

```css
.navbar                /* Navigation bar */
/* Navigation bar */
.navbar-brand          /* Brand/logo */
.navbar-nav            /* Nav items container */
.navbar-dropdown; /* Dropdown menu */
```

### 4. Layout System (\_layout.css)

**Grid de 12 columnas:**

```css
.container             /* Centered container */
.row                   /* Row wrapper */
.col-{1-12}           /* Column sizes */
.col-md-{1-12}        /* Responsive columns */
```

**Flexbox utilities:**

```css
.d-flex               /* Display flex */
.flex-row / .flex-column
.justify-{start|center|end|between|around}
.align-{start|center|end}
```

**Spacing utilities:**

```css
.m-{0-5}              /* Margin */
.mt-{0-5}             /* Margin top */
.p-{0-5}              /* Padding */
.px-{0-5}             /* Padding horizontal */
```

### 5. Utilities (\_utilities.css)

- Clases helper para casos comunes
- Shadows, borders, rounded corners
- Display utilities (d-none, d-block, etc.)
- Text utilities (text-center, text-muted, etc.)
- Animations (fade-in, slide-up, spinner)

## Arquitectura JavaScript

### 1. Capa de Utilidades (utils/)

**API (api.js):**

```javascript
API.get(url); // GET request
API.post(url, data); // POST request
API.put(url, data); // PUT request
API.delete(url); // DELETE request
API.uploadFile(url, file, field); // File upload
```

**Storage (storage.js):**

```javascript
Storage.get(key, defaultValue); // Get from localStorage
Storage.set(key, value); // Save to localStorage
Storage.remove(key); // Remove item
Storage.clear(); // Clear all
```

**Validator (validation.js):**

```javascript
Validator.isValidEmail(email);
Validator.isValidPassword(password);
Validator.isValidCedula(cedula); // Ecuadorian ID
Validator.validateForm(data, rules);
```

**Notify (notify.js):**

```javascript
Notify.success(message);
Notify.error(message);
Notify.warning(message);
Notify.confirm(message);
Notify.toast(message, type);
```

### 2. Capa de Módulos (modules/)

**Cart (cart.js):**

- Gestión del carrito de compras
- Persistencia en localStorage
- Sincronización con backend
- Actualización de UI

**Auth (auth.js):**

- Login y registro de usuarios
- Validación de formularios
- Manejo de sesiones

**Products (products.js):**

- Visualización de productos
- Filtrado y búsqueda
- Agregar al carrito

### 3. Scripts por Página

Cada página tiene su propio script que:

- Inicializa componentes específicos
- Maneja eventos de la página
- Coordina módulos y utilidades

## Patrones de Diseño

### 1. Separation of Concerns

- **CSS**: Solo estilos, sin lógica
- **HTML**: Solo estructura, eventos mínimos
- **JavaScript**: Toda la lógica

### 2. DRY (Don't Repeat Yourself)

- Estilos comunes en módulos reutilizables
- Funcionalidad común en utilidades
- Tokens de diseño en variables CSS

### 3. Progressive Enhancement

- La aplicación funciona sin JavaScript (formularios básicos)
- JavaScript mejora la experiencia (validación, AJAX, animaciones)

### 4. Mobile-First

- Estilos base para móviles
- Media queries para pantallas más grandes
- Grid responsive

### 5. Modular Architecture

- Cada módulo tiene una responsabilidad clara
- Módulos independientes y reutilizables
- Fácil de mantener y testear

## Sistema de Temas

### Implementación

El tema se controla mediante la clase `dark-mode` en el elemento `<body>`:

```javascript
// Toggle theme
document.body.classList.toggle("dark-mode");

// Save preference
localStorage.setItem("theme", isDark ? "dark" : "light");
```

### Variables Temáticas

Todas las variables de color se redefinen en el tema oscuro:

```css
:root {
  --color-bg: #ffffff;
  --color-text: #333333;
}

body.dark-mode {
  --color-bg: #1e1e1e;
  --color-text: #f5f5dc;
}
```

## Guías de Uso

### Agregar Nuevos Estilos

1. **Estilos Globales**: Agregar a los módulos correspondientes (\_buttons.css, \_forms.css, etc.)
2. **Estilos de Página**: Crear archivo CSS específico (nombre-pagina.css)
3. **Variables**: Definir nuevos tokens en \_variables.css

### Agregar Nueva Funcionalidad

1. **Utilidad General**: Agregar a utils/ si es reutilizable
2. **Funcionalidad de Módulo**: Extender módulo existente o crear nuevo en modules/
3. **Funcionalidad de Página**: Agregar a script específico de la página

### Estructura de un Módulo JavaScript

```javascript
/**
 * Module Name - Description
 */

class ModuleName {
  /**
   * Static method description
   * @param {Type} param - Parameter description
   * @returns {Type} Return description
   */
  static methodName(param) {
    // Implementation
  }
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  ModuleName.init();
});

// Export for use in other modules
if (typeof module !== "undefined" && module.exports) {
  module.exports = ModuleName;
}
```

## Dependencias Externas

- **Bootstrap 5**: Framework CSS base
- **SweetAlert2**: Notificaciones elegantes
- **Font Awesome**: Iconos
- **Google Fonts**: Tipografía (Pacifico)

## Mejores Prácticas

### CSS

1. Usar variables CSS en lugar de valores hardcoded
2. Seguir nomenclatura BEM para clases específicas
3. Mantener especificidad baja
4. Usar clases utilitarias para casos simples
5. Agrupar media queries al final del archivo

### JavaScript

1. Usar clases para agrupar funcionalidad relacionada
2. Documentar con JSDoc
3. Manejar errores apropiadamente
4. Usar async/await para operaciones asíncronas
5. Validar inputs del usuario

### General

1. Comentar código complejo
2. Mantener archivos pequeños y enfocados
3. Testear en múltiples navegadores
4. Optimizar imágenes
5. Minimizar archivos para producción

## Checklist de Desarrollo

### Nueva Página

- [ ] Crear HTML template en templates/
- [ ] Crear CSS específico en static/css/
- [ ] Importar main.css en el template
- [ ] Crear JS específico si es necesario
- [ ] Importar utilidades y módulos necesarios
- [ ] Testear responsive design
- [ ] Testear tema oscuro
- [ ] Validar accesibilidad

### Nuevo Componente

- [ ] Definir estructura HTML
- [ ] Crear estilos en módulo correspondiente
- [ ] Documentar variantes y estados
- [ ] Agregar ejemplo de uso
- [ ] Testear en diferentes contextos

### Nueva Funcionalidad

- [ ] Identificar si es utilidad o módulo
- [ ] Implementar con manejo de errores
- [ ] Documentar con JSDoc
- [ ] Agregar validaciones necesarias
- [ ] Testear casos edge

## Roadmap Futuro

### Corto Plazo

- [ ] Webpack/Vite para bundling
- [ ] CSS preprocessing (Sass/PostCSS)
- [ ] Lazy loading de imágenes
- [ ] Service Worker para PWA

### Mediano Plazo

- [ ] Tests unitarios (Jest)
- [ ] Tests E2E (Playwright)
- [ ] Optimización de performance
- [ ] Análisis de accesibilidad (a11y)

### Largo Plazo

- [ ] Migración a framework moderno (React/Vue)
- [ ] TypeScript para type safety
- [ ] Component library (Storybook)
- [ ] Design system documentation

## Recursos

- [MDN Web Docs](https://developer.mozilla.org/)
- [CSS Tricks](https://css-tricks.com/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)
- [SweetAlert2 Documentation](https://sweetalert2.github.io/)
