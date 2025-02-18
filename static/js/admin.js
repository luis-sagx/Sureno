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

function updateOrderStatus(orderId, newStatus) {
    fetch(`/api/orders/${orderId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ estado: newStatus })
    })
    .then(response => response.json())
    .then(data => {
      if (data.message) {
        alert(data.message);
      } else {
        alert(data.error);
      }
    })
    .catch(error => console.error('Error:', error));
}

function deleteOrder(orderId) {
    if (confirm('¿Estás seguro de que deseas eliminar este pedido?')) {
        fetch(`/api/orders/${orderId}`, {
        method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
        if (data.message) {
            alert(data.message);
            window.location.reload();
        } else {
            alert(data.error);
        }
        })
        .catch(error => console.error('Error:', error));
    }
}

function abrirModalBuscarDireccion() {
    document.getElementById('txtDireccionId').value = '';
    document.getElementById('resultadoDireccion').innerHTML = '';
    const modal = new bootstrap.Modal(document.getElementById('modalBuscarDireccion'));
    modal.show();
}

function buscarDireccion() {
    const direccionId = document.getElementById('txtDireccionId').value.trim();
    if (!direccionId) {
      alert('Por favor, ingresa un ID válido.');
      return;
    }
  
    fetch(`/api/addresses/${direccionId}`)
      .then(response => {
        if (!response.ok) {
          throw new Error('Error en la respuesta del servidor');
        }
        return response.json();
      })
      .then(data => {
        const resultadoDiv = document.getElementById('resultadoDireccion');
        if (data.error) {
          resultadoDiv.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
        } else {
          resultadoDiv.innerHTML = `
            <div class="alert alert-success">
              <strong>Dirección encontrada:</strong><br>
              <strong>Provincia:</strong> ${data.provincia}<br>
              <strong>Cantón:</strong> ${data.canton}<br>
              <strong>Parroquia:</strong> ${data.parroquia}<br>
              <strong>Calle Principal:</strong> ${data.calle_principal}<br>
              <strong>Calle Secundaria:</strong> ${data.calle_secundaria}<br>
              <strong>Código Postal:</strong> ${data.codigo_postal}<br>
            </div>
          `;
        }
      })
      .catch(error => {
        console.error('Error:', error);
        document.getElementById('resultadoDireccion').innerHTML = `
          <div class="alert alert-danger">Error al buscar la dirección: ${error.message}</div>
        `;
    });
}