# Sureno

Sureno es un sitio web de comercio electrónico para la empresa Sureño, la cual se encarga de vender licores de su marca. El proyecto fue desarrollado utilizando el framework Flask de Python. Este proyecto tiene como objetivo proporcionar una plataforma donde los usuarios pueden explorar, seleccionar y comprar productos de manera sencilla y eficiente.

## Partes del Sitio

- **Clientes**: Los clientes pueden registrarse, navegar por los productos, añadirlos al carrito y realizar compras.
- **Administradores**: Los administradores tienen acceso a un panel de control donde pueden gestionar todos los aspectos del sitio, incluyendo la gestión de productos y la visualización de pedidos.

## Credenciales de Acceso

- **Administrador**:
  - **Usuario**: adminSureno@gmail.com
  - **Contraseña**: admin1

- **Cliente**:
  - **Usuario**: ingresoSureno@gmail.com
  - **Contraseña**: ingreso1

## Características

- **Registro y Autenticación de Usuarios**: Permite a los usuarios registrarse y acceder a sus cuentas. Hay roles diferenciados para administradores y clientes.
- **Gestión de Productos**: Los administradores pueden agregar, editar y eliminar productos de la base de datos, asegurando que el catálogo esté siempre actualizado.
- **Carrito de Compras**: Los usuarios pueden añadir productos a su carrito y gestionar su selección antes de proceder al pago.
- **Proceso de Pago**: Integración de un sistema de pago seguro para facilitar la compra de productos.
- **Historial de Pedidos**: Los usuarios pueden consultar el historial de sus pedidos anteriores.

## Tecnologías Utilizadas

- **Lenguaje de Programación**: Python
- **Framework**: Flask
- **Frontend**: HTML, CSS, JavaScript
- **Base de Datos**: MongoDB Atlas

## Instalación

Para instalar y ejecutar el proyecto en tu máquina local, sigue estos pasos:

1. Clona el repositorio:
   ```bash
   git clone https://github.com/luis-sagx/Sureno.git
   ```
2. Navega al directorio del proyecto:
  ```bash
   cd Sureno
  ```
3. Instala las dependencias:
  ```bash
   pip install -r requirements.txt
  ```
4. Ejecuta la aplicación:
  ```bash
   python app.py
  ```

## SonarQube Cloud sin tests

Si el proyecto usa **Automatic analysis** en SonarQube Cloud, la cobertura **no está soportada** y por eso no aparece `0%`; en su lugar, Sonar muestra que falta configurar coverage.

Para que se vea `0%` de cobertura en este proyecto:

1. Desactiva `Automatic analysis` en SonarQube Cloud y usa análisis por scanner/CI.
2. Genera un reporte vacío de cobertura:
   ```bash
   python scripts/generate_empty_coverage.py
   ```
3. Ejecuta el análisis de Sonar con el archivo `coverage.xml` generado.

El archivo `sonar-project.properties` ya apunta a:

```properties
sonar.python.coverage.reportPaths=coverage.xml
```

Si ejecutas `sonar-scanner` o el workflow de GitHub Actions con ese reporte, SonarQube Cloud podrá importar cobertura y mostrará el proyecto con cobertura en `0%` mientras no existan tests.

### GitHub Actions

El repositorio ya incluye el workflow:

```text
.github/workflows/sonar.yml
```

Antes de usarlo, en GitHub debes configurar:

- `Settings > Secrets and variables > Actions > Secrets`
  - `SONAR_TOKEN`
- `Settings > Secrets and variables > Actions > Variables`
  - `SONAR_PROJECT_KEY`
  - `SONAR_ORGANIZATION`

Luego:

1. Desactiva `Automatic Analysis` en SonarQube Cloud.
2. Haz commit y push de estos cambios.
3. GitHub Actions ejecutará el análisis y enviará el resultado a SonarQube Cloud.
