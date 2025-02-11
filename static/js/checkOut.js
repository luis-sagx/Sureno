document.getElementById('address-form').addEventListener('submit', function(e) {
    e.preventDefault(); // Evita el envío tradicional del formulario

    // Extraer los valores de cada campo
    const provincia = document.getElementById('provincia').value;
    const canton = document.getElementById('canton').value;
    const parroquia = document.getElementById('parroquia').value;
    const calle_principal = document.getElementById('calle_principal').value;
    const calle_secundaria = document.getElementById('calle_secundaria').value;
    const codigo_postal = document.getElementById('codigo_postal').value;

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
            // Opcional: Notificar al usuario, redirigir o limpiar el formulario
            // Por ejemplo, redireccionar a otra sección de checkout:
            // window.location.href = '/checkout-final';
        })
        .catch(error => {
            console.error('Error al guardar la dirección:', error);
        });
});