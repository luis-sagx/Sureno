/**
 * Notification Utilities - User notifications and alerts
 */

class Notify {
    /**
     * Show success notification
     * @param {string} message - Message to display
     * @param {Object} options - SweetAlert2 options
     */
    static success(message, options = {}) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'success',
                title: options.title || '¡Éxito!',
                text: message,
                showConfirmButton: false,
                timer: options.timer || 2000,
                ...options
            });
        } else {
            alert(message);
        }
    }

    /**
     * Show error notification
     * @param {string} message - Message to display
     * @param {Object} options - SweetAlert2 options
     */
    static error(message, options = {}) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'error',
                title: options.title || 'Error',
                text: message,
                confirmButtonText: 'Aceptar',
                ...options
            });
        } else {
            alert('Error: ' + message);
        }
    }

    /**
     * Show warning notification
     * @param {string} message - Message to display
     * @param {Object} options - SweetAlert2 options
     */
    static warning(message, options = {}) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'warning',
                title: options.title || 'Advertencia',
                text: message,
                confirmButtonText: 'Aceptar',
                ...options
            });
        } else {
            alert('Advertencia: ' + message);
        }
    }

    /**
     * Show info notification
     * @param {string} message - Message to display
     * @param {Object} options - SweetAlert2 options
     */
    static info(message, options = {}) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'info',
                title: options.title || 'Información',
                text: message,
                confirmButtonText: 'Aceptar',
                ...options
            });
        } else {
            alert(message);
        }
    }

    /**
     * Show confirmation dialog
     * @param {string} message - Message to display
     * @param {Object} options - SweetAlert2 options
     * @returns {Promise<boolean>} True if confirmed
     */
    static async confirm(message, options = {}) {
        if (typeof Swal !== 'undefined') {
            const result = await Swal.fire({
                icon: 'question',
                title: options.title || '¿Estás seguro?',
                text: message,
                showCancelButton: true,
                confirmButtonText: options.confirmText || 'Sí, confirmar',
                cancelButtonText: options.cancelText || 'Cancelar',
                confirmButtonColor: '#906243',
                cancelButtonColor: '#6c757d',
                ...options
            });
            return result.isConfirmed;
        } else {
            return confirm(message);
        }
    }

    /**
     * Show loading notification
     * @param {string} message - Message to display
     */
    static loading(message = 'Cargando...') {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: message,
                allowOutsideClick: false,
                allowEscapeKey: false,
                showConfirmButton: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });
        }
    }

    /**
     * Close notification
     */
    static close() {
        if (typeof Swal !== 'undefined') {
            Swal.close();
        }
    }

    /**
     * Show toast notification
     * @param {string} message - Message to display
     * @param {string} type - Type: success, error, warning, info
     * @param {Object} options - Additional options
     */
    static toast(message, type = 'success', options = {}) {
        if (typeof Swal !== 'undefined') {
            const Toast = Swal.mixin({
                toast: true,
                position: options.position || 'top-end',
                showConfirmButton: false,
                timer: options.timer || 3000,
                timerProgressBar: true,
                didOpen: (toast) => {
                    toast.addEventListener('mouseenter', Swal.stopTimer);
                    toast.addEventListener('mouseleave', Swal.resumeTimer);
                }
            });

            Toast.fire({
                icon: type,
                title: message,
                ...options
            });
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Notify;
}
