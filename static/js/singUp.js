const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async(e) => {
        e.preventDefault();

        const userData = {
            nombre: document.getElementById('nombre').value,
            apellido: document.getElementById('apellido').value,
            email: document.getElementById('email').value,
            password: document.getElementById('password').value,
            cedula: document.getElementById('cedula').value
        };

        try {
            const response = await fetch('/signUp', { //  Corregida la ruta
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            const result = await response.json();

            if (response.ok) {
                alert('Registro exitoso!');
                window.location.href = "{{ url_for('login') }}"; // Redirigir después del registro
            } else {
                alert(`Error: ${result.error}`);
            }
        } catch (error) {
            alert('Error de conexión');
        }
    });
}