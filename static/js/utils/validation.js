/**
 * Validation Utilities - Form and data validation
 */

class Validator {
    /**
     * Validate email format
     * @param {string} email - Email to validate
     * @returns {boolean} True if valid
     */
    static isValidEmail(email) {
        const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return regex.test(email);
    }

    /**
     * Validate password strength
     * @param {string} password - Password to validate
     * @param {number} minLength - Minimum length (default: 6)
     * @returns {Object} Validation result with isValid and message
     */
    static isValidPassword(password, minLength = 6) {
        if (!password || password.length < minLength) {
            return {
                isValid: false,
                message: `La contraseña debe tener al menos ${minLength} caracteres`
            };
        }
        return { isValid: true, message: 'Contraseña válida' };
    }

    /**
     * Validate Ecuadorian cedula
     * @param {string} cedula - Cedula to validate
     * @returns {boolean} True if valid
     */
    static isValidCedula(cedula) {
        if (!cedula || !/^\d{10}$/.test(cedula)) {
            return false;
        }

        const digits = cedula.split('').map(Number);
        const province = parseInt(cedula.substring(0, 2));

        if (province < 1 || province > 24) {
            return false;
        }

        // Validate check digit
        const coefficients = [2, 1, 2, 1, 2, 1, 2, 1, 2];
        let sum = 0;

        for (let i = 0; i < 9; i++) {
            let product = digits[i] * coefficients[i];
            if (product >= 10) product -= 9;
            sum += product;
        }

        const checkDigit = sum % 10 === 0 ? 0 : 10 - (sum % 10);
        return checkDigit === digits[9];
    }

    /**
     * Validate phone number
     * @param {string} phone - Phone to validate
     * @returns {boolean} True if valid
     */
    static isValidPhone(phone) {
        // Ecuadorian phone format: 09XXXXXXXX or 02XXXXXXX
        const regex = /^0[2-9]\d{7,8}$/;
        return regex.test(phone);
    }

    /**
     * Validate required field
     * @param {*} value - Value to validate
     * @returns {boolean} True if not empty
     */
    static isRequired(value) {
        if (value === null || value === undefined) return false;
        if (typeof value === 'string') return value.trim().length > 0;
        if (Array.isArray(value)) return value.length > 0;
        return true;
    }

    /**
     * Validate number range
     * @param {number} value - Value to validate
     * @param {number} min - Minimum value
     * @param {number} max - Maximum value
     * @returns {boolean} True if in range
     */
    static isInRange(value, min, max) {
        const num = parseFloat(value);
        return !isNaN(num) && num >= min && num <= max;
    }

    /**
     * Validate positive number
     * @param {number} value - Value to validate
     * @returns {boolean} True if positive
     */
    static isPositive(value) {
        const num = parseFloat(value);
        return !isNaN(num) && num > 0;
    }

    /**
     * Validate form fields
     * @param {Object} formData - Form data to validate
     * @param {Object} rules - Validation rules
     * @returns {Object} Validation result with errors
     */
    static validateForm(formData, rules) {
        const errors = {};

        for (const [field, rule] of Object.entries(rules)) {
            const value = formData[field];

            if (rule.required && !this.isRequired(value)) {
                errors[field] = `${rule.label || field} es requerido`;
                continue;
            }

            if (value && rule.type === 'email' && !this.isValidEmail(value)) {
                errors[field] = 'Email inválido';
            }

            if (value && rule.type === 'cedula' && !this.isValidCedula(value)) {
                errors[field] = 'Cédula inválida';
            }

            if (value && rule.type === 'phone' && !this.isValidPhone(value)) {
                errors[field] = 'Teléfono inválido';
            }

            if (value && rule.minLength && value.length < rule.minLength) {
                errors[field] = `Mínimo ${rule.minLength} caracteres`;
            }

            if (value && rule.maxLength && value.length > rule.maxLength) {
                errors[field] = `Máximo ${rule.maxLength} caracteres`;
            }

            if (value && rule.min !== undefined && !this.isInRange(value, rule.min, Infinity)) {
                errors[field] = `Mínimo ${rule.min}`;
            }

            if (value && rule.max !== undefined && !this.isInRange(value, -Infinity, rule.max)) {
                errors[field] = `Máximo ${rule.max}`;
            }
        }

        return {
            isValid: Object.keys(errors).length === 0,
            errors
        };
    }

    /**
     * Show validation errors in form
     * @param {Object} errors - Errors object
     */
    static showFormErrors(errors) {
        // Clear previous errors
        document.querySelectorAll('.invalid-feedback').forEach(el => {
            el.textContent = '';
        });
        document.querySelectorAll('.form-control').forEach(el => {
            el.classList.remove('is-invalid');
        });

        // Show new errors
        for (const [field, message] of Object.entries(errors)) {
            const input = document.getElementById(field) || document.querySelector(`[name="${field}"]`);
            if (input) {
                input.classList.add('is-invalid');
                const feedback = input.parentElement.querySelector('.invalid-feedback');
                if (feedback) {
                    feedback.textContent = message;
                } else {
                    const feedbackEl = document.createElement('div');
                    feedbackEl.className = 'invalid-feedback';
                    feedbackEl.textContent = message;
                    input.parentElement.appendChild(feedbackEl);
                }
            }
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Validator;
}
