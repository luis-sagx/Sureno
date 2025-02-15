function cargarProducto(id, nombre, precio, stock, mililitros, imagen) {
    document.getElementById('editProductId').value = id;
    document.getElementById('editNombre').value = nombre;
    document.getElementById('editPrecio').value = precio;
    document.getElementById('editStock').value = stock;
    document.getElementById('editMililitros').value = mililitros;
    document.getElementById('editImagen').value = imagen;
}

document.getElementById('formEditarProducto').addEventListener('submit', function(event) {
    event.preventDefault();
    
    let id = document.getElementById('editProductId').value;
    let data = {
        nombre: document.getElementById('editNombre').value,
        precio: document.getElementById('editPrecio').value,
        stock: document.getElementById('editStock').value,
        mililitros: document.getElementById('editMililitros').value,
        imagen: document.getElementById('editImagen').value
    };

    fetch(`/api/products/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert("Producto actualizado con éxito");
            location.reload();
        } else {
            alert("Error al actualizar el producto");
        }
    });
});

function eliminarProducto() {
    let id = document.getElementById('deleteProductId').value;
    fetch(`/api/products/${id}`, { method: "DELETE" })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert("Producto eliminado con éxito");
            location.reload();
        } else {
            alert("Error al eliminar el producto");
        }
    });
}