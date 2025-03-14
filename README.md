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
