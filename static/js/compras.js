// Función para mostrar notificaciones estilizadas
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'} me-2"></i>
        ${message}
    `;

    document.body.appendChild(notification);

    // Animación de entrada
    setTimeout(() => notification.classList.add('show'), 100);

    // Eliminar después de 3 segundos
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 500);
    }, 3000);
}

// Función principal para cancelar pedido
async function cancelOrder(orderId) {
    try {
        const response = await fetch(`/api/orders/${orderId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'include'
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Error al eliminar');
        }

        // Eliminar fila de la tabla
        document.querySelector(`[data-order-id="${orderId}"]`).closest('tr').remove();

        // Mostrar notificación
        Swal.fire({
            icon: 'success',
            title: '¡Eliminado!',
            text: 'El pedido fue eliminado correctamente',
            confirmButtonColor: 'var(--boton-cafe)'
        });

    } catch (error) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message,
            confirmButtonColor: 'var(--naranja)'
        });
    }
}