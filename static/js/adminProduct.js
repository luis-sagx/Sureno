function cargarProducto(id, nombre, precio, stock, mililitros, imagen, categoria_id) {
    document.getElementById('editProductId').value = id;
    document.getElementById('editNombre').value = nombre;
    document.getElementById('editPrecio').value = precio;
    document.getElementById('editStock').value = stock;
    document.getElementById('editMililitros').value = mililitros;
    //document.getElementById('editImagen').value = imagen;
    document.getElementById('editCategoriaId').value = categoria_id; // Cargar categoría
}

document.getElementById('formAgregarProducto').addEventListener('submit', function(event) {
    event.preventDefault();
    
    const formData = new FormData();
    formData.append('nombre', document.getElementById('addNombre').value);
    formData.append('precio', document.getElementById('addPrecio').value);
    formData.append('stock', document.getElementById('addStock').value);
    formData.append('mililitros', document.getElementById('addMililitros').value);
    formData.append('categoria_id', document.getElementById('addCategoriaId').value);
    
    const imageFile = document.getElementById('addImagen').files[0];
    if (imageFile) {
        formData.append('imagen', imageFile);
    }

    fetch('/api/products', {
        method: 'POST',
        body: formData // No incluir Content-Type header, let browser set it
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert(data.message || "Producto agregado exitosamente");
            location.reload();
        }
    })
    .catch(error => {
        console.error("Error al agregar producto:", error);
        alert("Error al agregar producto");
    });
});

document.getElementById('formEditarProducto').addEventListener('submit', function(event) {
    event.preventDefault();
    
    const formData = new FormData();
    formData.append('nombre', document.getElementById('editNombre').value);
    formData.append('precio', document.getElementById('editPrecio').value);
    formData.append('stock', document.getElementById('editStock').value);
    formData.append('mililitros', document.getElementById('editMililitros').value);
    formData.append('categoria_id', document.getElementById('editCategoriaId').value);
    
    const imageFile = document.getElementById('editImagen').files[0];
    if (imageFile) {
        formData.append('imagen', imageFile);
    }

    const productId = document.getElementById('editProductId').value;

    fetch(`/api/products/${productId}`, {
        method: 'PUT',
        body: formData  // No incluir Content-Type header para que el navegador lo maneje
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert(data.message || "Producto actualizado exitosamente");
            location.reload();
        }
    })
    .catch(error => {
        console.error("Error al actualizar producto:", error);
        alert("Error al actualizar producto: " + error.message);
    });
});

function eliminarProducto() {
    let id = document.getElementById('deleteProductId').value;
    if (!id) {
        alert("Error: ID de producto no encontrado");
        return;
    }
    fetch(`/api/products/${id}`, { method: "DELETE" })
    .then(response => response.json())
    .then(data => {
        alert(data.message || "Producto eliminado");
        location.reload();
    })
    .catch(error => alert("Error al eliminar"));
}