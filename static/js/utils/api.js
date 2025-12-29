/**
 * API Utilities - Centralized API communication
 */

class API {
    /**
     * Make a GET request
     * @param {string} url - The endpoint URL
     * @param {Object} options - Additional fetch options
     * @returns {Promise<Object>} Response data
     */
    static async get(url, options = {}) {
        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            return await this.handleResponse(response);
        } catch (error) {
            return this.handleError(error);
        }
    }

    /**
     * Make a POST request
     * @param {string} url - The endpoint URL
     * @param {Object} data - Data to send
     * @param {Object} options - Additional fetch options
     * @returns {Promise<Object>} Response data
     */
    static async post(url, data, options = {}) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                body: JSON.stringify(data),
                ...options
            });

            return await this.handleResponse(response);
        } catch (error) {
            return this.handleError(error);
        }
    }

    /**
     * Make a PUT request
     * @param {string} url - The endpoint URL
     * @param {Object} data - Data to send
     * @param {Object} options - Additional fetch options
     * @returns {Promise<Object>} Response data
     */
    static async put(url, data, options = {}) {
        try {
            const response = await fetch(url, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                body: JSON.stringify(data),
                ...options
            });

            return await this.handleResponse(response);
        } catch (error) {
            return this.handleError(error);
        }
    }

    /**
     * Make a DELETE request
     * @param {string} url - The endpoint URL
     * @param {Object} options - Additional fetch options
     * @returns {Promise<Object>} Response data
     */
    static async delete(url, options = {}) {
        try {
            const response = await fetch(url, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            return await this.handleResponse(response);
        } catch (error) {
            return this.handleError(error);
        }
    }

    /**
     * Handle fetch response
     * @param {Response} response - Fetch response
     * @returns {Promise<Object>} Parsed response
     */
    static async handleResponse(response) {
        const contentType = response.headers.get('content-type');
        const isJson = contentType && contentType.includes('application/json');

        const data = isJson ? await response.json() : await response.text();

        if (!response.ok) {
            const error = (data && data.error) || response.statusText;
            return Promise.reject({
                status: response.status,
                message: error,
                data: data
            });
        }

        return data;
    }

    /**
     * Handle fetch error
     * @param {Error} error - Error object
     * @returns {Promise} Rejected promise with error
     */
    static handleError(error) {
        console.error('API Error:', error);
        return Promise.reject({
            status: 500,
            message: error.message || 'Error de conexión con el servidor',
            data: null
        });
    }

    /**
     * Upload a file
     * @param {string} url - The endpoint URL
     * @param {FormData} formData - Form data with file
     * @param {Object} options - Additional fetch options
     * @returns {Promise<Object>} Response data
     */
    static async uploadFile(url, formData, options = {}) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                ...options
            });

            return await this.handleResponse(response);
        } catch (error) {
            return this.handleError(error);
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = API;
}
