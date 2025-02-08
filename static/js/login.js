document.addEventListener("DOMContentLoaded", function() {
    const loginForm = document.getElementById("loginForm");

    loginForm.addEventListener("submit", async(e) => {
        e.preventDefault();

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        const userData = { email, password };

        try {
            const response = await fetch("/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(userData),
            });

            const result = await response.json();

            if (response.ok) {
                alert("Inicio de sesión exitoso!");
                window.location.href = result.redirect; // Redirige a index.html
            } else {
                alert(`Error: ${result.error}`);
            }
        } catch (error) {
            alert("Error de conexión con el servidor");
        }
    });
});