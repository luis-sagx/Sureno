const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async(e) => {
        e.preventDefault();
        const userData = {
            email: document.getElementById('email').value,
            password: document.getElementById('password').value,
            cedula: document.getElementById('cedula').value,
            fecha_nacimiento: document.getElementById('fecha_nacimiento').value
        };
        try {
            const response = await fetch('/singUp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });
            const result = await response.json();
            if (response.ok) {
                alert('Registro exitoso!');
                window.location.href = '/login'; // Redirigir después del registro
            } else {
                alert(`Error: ${result.error}`);
            }
        } catch (error) {
            alert('Error de conexión');
        }
    });
}