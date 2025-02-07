document.addEventListener("DOMContentLoaded", function () {
    actualizarCarritoUI();
});

function agregarAlCarrito(id, nombre, precio, imagen, mililitros) {
    let carrito = JSON.parse(localStorage.getItem("carrito")) || [];
    
    let productoExistente = carrito.find(p => p.id === id);
    
    if (productoExistente) {
        productoExistente.cantidad++;
    } else {
        carrito.push({ id, nombre, precio: parseFloat(precio), imagen, mililitros, cantidad: 1 });
    }

    localStorage.setItem("carrito", JSON.stringify(carrito));

    // Actualizar el icono del carrito
    actualizarCarritoUI();

    // Animación en el icono del carrito
    let cartIcon = document.getElementById("cart-icon");
    cartIcon.classList.add("cart-animate");
    setTimeout(() => cartIcon.classList.remove("cart-animate"), 300);

    // Notificación con SweetAlert
    Swal.fire({
        title: "Producto agregado",
        text: `"${nombre}" ha sido añadido al carrito.`,
        icon: "success",
        showConfirmButton: false,
        timer: 2000
    });
}

function actualizarCarritoUI() {
    let carrito = JSON.parse(localStorage.getItem("carrito")) || [];
    let totalProductos = carrito.reduce((total, p) => total + p.cantidad, 0);
    
    let cartCount = document.getElementById("cart-count");
    cartCount.innerText = totalProductos;
    cartCount.style.display = totalProductos > 0 ? "inline-block" : "none";
}


function cargarCarrito() {
    let carrito = JSON.parse(localStorage.getItem("carrito")) || [];
    let cartItemsContainer = document.getElementById("cart-items");
    let totalPrice = 0;
    
    cartItemsContainer.innerHTML = "";

    if (carrito.length === 0) {
        contenedor.innerHTML += `<p class="empty-cart">Tu carrito está vacío.</p>`;
        actualizarTotal(0); // Asegurar que el total sea $0.00
        return;
    }

    carrito.forEach((producto, index) => {
        totalPrice += producto.precio * producto.cantidad;

        cartItemsContainer.innerHTML += `
            <div class="cart-item">
                <img src="${producto.imagen}" alt="${producto.nombre}">
                <div class="item-details">
                    <h2>${producto.nombre}</h2>
                    <p>${producto.mililitros} ml</p>
                    <span class="price">$${(producto.precio * producto.cantidad).toFixed(2)}</span>
                    <div class="quantity-box">
                        <button class="quantity-btn" onclick="actualizarCantidad(${index}, -1)">-</button>
                        <input type="number" value="${producto.cantidad}" class="quantity-input" readonly>
                        <button class="quantity-btn" onclick="actualizarCantidad(${index}, 1)">+</button>
                    </div>
                </div>
                <button class="remove-btn" onclick="eliminarDelCarrito(${index})">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </div>
            <hr>
        `;
    });

    document.getElementById("total-price").innerText = `$${totalPrice.toFixed(2)}`;
}

function actualizarCantidad(index, cambio) {
    let carrito = JSON.parse(localStorage.getItem("carrito")) || [];

    if (carrito[index].cantidad + cambio > 0) {
        carrito[index].cantidad += cambio;
    } else {
        carrito.splice(index, 1); // Si la cantidad es 0, se elimina el producto
    }

    localStorage.setItem("carrito", JSON.stringify(carrito));
    cargarCarrito();
}

function eliminarDelCarrito(index) {
    let carrito = JSON.parse(localStorage.getItem("carrito")) || [];
    carrito.splice(index, 1);  // Eliminar el producto del carrito

    localStorage.setItem("carrito", JSON.stringify(carrito)); // Guardar cambios
    cargarCarrito(); // Volver a cargar los productos y recalcular el total
}

document.addEventListener("DOMContentLoaded", cargarCarrito);