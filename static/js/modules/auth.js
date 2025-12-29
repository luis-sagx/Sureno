/**
 * Auth Module - Authentication functionality
 */

class Auth {
    /**
     * Login user
     * @param {Object} credentials - Email and password
     * @returns {Promise<Object>} API response
     */
    static async login(credentials) {
        try {
            const result = await API.post('/api/auth/login', credentials);
            return { success: true, data: result };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    /**
     * Register user
     * @param {Object} userData - User registration data
     * @returns {Promise<Object>} API response
     */
    static async register(userData) {
        try {
            const result = await API.post('/api/auth/register', userData);
            return { success: true, data: result };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    /**
     * Logout user
     * @returns {Promise<Object>} API response
     */
    static async logout() {
        try {
            await API.post('/api/auth/logout');
            Cart.clear(); // Clear cart on logout
            window.location.href = '/login';
            return { success: true };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    /**
     * Get current user
     * @returns {Promise<Object>} User data
     */
    static async getCurrentUser() {
        try {
            const user = await API.get('/api/user');
            return { success: true, data: user };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    /**
     * Initialize login form
     */
    static initLoginForm() {
        const form = document.getElementById('loginForm');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            // Validate
            const validation = Validator.validateForm(
                { email, password },
                {
                    email: { required: true, type: 'email', label: 'Email' },
                    password: { required: true, minLength: 6, label: 'Contraseña' }
                }
            );

            if (!validation.isValid) {
                Validator.showFormErrors(validation.errors);
                return;
            }

            // Login
            Notify.loading('Iniciando sesión...');
            const result = await Auth.login({ email, password });

            if (result.success) {
                Notify.success('¡Inicio de sesión exitoso!');
                setTimeout(() => {
                    window.location.href = result.data.redirect || '/index';
                }, 1500);
            } else {
                Notify.close();
                Notify.error(result.error || 'Error al iniciar sesión');
            }
        });
    }

    /**
     * Initialize register form
     */
    static initRegisterForm() {
        const form = document.getElementById('signUpForm');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(form);
            const userData = Object.fromEntries(formData);

            // Validate
            const validation = Validator.validateForm(userData, {
                email: { required: true, type: 'email', label: 'Email' },
                nombre: { required: true, label: 'Nombre' },
                apellido: { required: true, label: 'Apellido' },
                password: { required: true, minLength: 6, label: 'Contraseña' },
                cedula: { required: true, type: 'cedula', label: 'Cédula' }
            });

            if (!validation.isValid) {
                Validator.showFormErrors(validation.errors);
                return;
            }

            // Register
            Notify.loading('Registrando usuario...');

            // Use traditional form submit for registration
            form.submit();
        });
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    Auth.initLoginForm();
    Auth.initRegisterForm();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Auth;
}
