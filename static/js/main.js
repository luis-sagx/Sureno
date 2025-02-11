document.addEventListener("DOMContentLoaded", function() {
    // Funciones y eventos del carrito (ya existentes)
    actualizarCarritoUI();
    cargarCarrito();

    // Evento para confirmar el carrito (ya implementado)
    const confirmarBtn = document.getElementById("confirmar-productos");
    if (confirmarBtn) {
        confirmarBtn.addEventListener("click", function(event) {
            event.preventDefault(); // Prevenir comportamiento por defecto
            enviarCarrito();
        });
    }

    // Nuevo: Asignar el evento submit al formulario de dirección
    const addressForm = document.getElementById("address-form");
    if (addressForm) {
        addressForm.addEventListener("submit", function(e) {
            e.preventDefault(); // Evita el envío tradicional del formulario

            // Extraer los valores de cada campo del formulario
            const provincia = document.getElementById("provincia").value;
            const canton = document.getElementById("canton").value;
            const parroquia = document.getElementById("parroquia").value;
            const calle_principal = document.getElementById("calle_principal").value;
            const calle_secundaria = document.getElementById("calle_secundaria").value;
            const codigo_postal = document.getElementById("codigo_postal").value;

            // Construir el objeto que se enviará al backend
            const addressData = {
                provincia: provincia,
                canton: canton,
                parroquia: parroquia,
                calle_principal: calle_principal,
                calle_secundaria: calle_secundaria,
                codigo_postal: parseInt(codigo_postal)
            };

            // Enviar la petición POST al backend para guardar la dirección
            fetch('/addresses', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(addressData)
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Dirección guardada:', data);
                    // Opcional:
                    // Aquí puedes redirigir, notificar al usuario o limpiar el formulario.
                    // Por ejemplo, redirigir de nuevo a la página del carrito:
                    window.location.href = "/cart";
                })
                .catch(error => {
                    console.error('Error al guardar la dirección:', error);
                });
        });
    }
});

// --- Funciones existentes para el carrito ---

function agregarAlCarrito(id, nombre, precio, imagen, mililitros) {
    let carrito = JSON.parse(localStorage.getItem("carrito")) || [];

    let productoExistente = carrito.find(p => p.id === id);
    if (productoExistente) {
        productoExistente.cantidad++;
    } else {
        carrito.push({ id, nombre, precio: parseFloat(precio), imagen, mililitros, cantidad: 1 });
    }

    localStorage.setItem("carrito", JSON.stringify(carrito));
    actualizarCarritoUI();

    let cartIcon = document.getElementById("cart-icon");
    if (cartIcon) {
        cartIcon.classList.add("cart-animate");
        setTimeout(() => cartIcon.classList.remove("cart-animate"), 300);
    }

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
    if (cartCount) {
        cartCount.innerText = totalProductos;
        cartCount.style.display = totalProductos > 0 ? "inline-block" : "none";
    }
}

function cargarCarrito() {
    let carrito = JSON.parse(localStorage.getItem("carrito")) || [];
    let cartItemsContainer = document.getElementById("cart-items");
    let totalPrice = 0;
    if (!cartItemsContainer) return;

    cartItemsContainer.innerHTML = "";

    if (carrito.length === 0) {
        cartItemsContainer.innerHTML = `<p class="empty-cart">Tu carrito está vacío.</p>`;
        document.getElementById("total-price").innerText = "$0.00";
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
        carrito.splice(index, 1);
    }
    localStorage.setItem("carrito", JSON.stringify(carrito));
    cargarCarrito();
}

function eliminarDelCarrito(index) {
    let carrito = JSON.parse(localStorage.getItem("carrito")) || [];
    carrito.splice(index, 1);
    localStorage.setItem("carrito", JSON.stringify(carrito));
    cargarCarrito();
}

function enviarCarrito() {
    let carrito = JSON.parse(localStorage.getItem("carrito")) || [];
    let total = carrito.reduce((sum, item) => sum + (item.precio * item.cantidad), 0);
    fetch('/cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ productos: carrito, total: total })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Carrito guardado:', data);
            localStorage.removeItem("carrito");
            window.location.href = "/checkOut";
        })
        .catch(error => {
            console.error('Error al guardar el carrito:', error);
        });
}