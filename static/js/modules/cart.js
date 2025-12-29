/**
 * Cart Module - Shopping cart functionality
 */

class Cart {
    static STORAGE_KEY = 'carrito';

    /**
     * Get cart from storage
     * @returns {Array} Cart items
     */
    static getItems() {
        return Storage.get(Cart.STORAGE_KEY, []);
    }

    /**
     * Save cart to storage
     * @param {Array} items - Cart items
     */
    static saveItems(items) {
        Storage.set(Cart.STORAGE_KEY, items);
    }

    /**
     * Add item to cart
     * @param {Object} product - Product to add
     * @returns {Array} Updated cart
     */
    static addItem(product) {
        const cart = this.getItems();
        const { id, nombre, precio, imagen, mililitros } = product;

        const existingItem = cart.find(item => item.id === id);

        if (existingItem) {
            existingItem.cantidad++;
        } else {
            cart.push({
                id,
                nombre,
                precio: parseFloat(precio),
                imagen,
                mililitros,
                cantidad: 1
            });
        }

        this.saveItems(cart);
        this.updateUI();
        return cart;
    }

    /**
     * Remove item from cart
     * @param {string} productId - Product ID to remove
     * @returns {Array} Updated cart
     */
    static removeItem(productId) {
        let cart = this.getItems();
        cart = cart.filter(item => item.id !== productId);

        this.saveItems(cart);
        this.updateUI();
        return cart;
    }

    /**
     * Update item quantity
     * @param {string} productId - Product ID
     * @param {number} quantity - New quantity
     * @returns {Array} Updated cart
     */
    static updateQuantity(productId, quantity) {
        const cart = this.getItems();
        const item = cart.find(item => item.id === productId);

        if (item) {
            item.cantidad = Math.max(1, parseInt(quantity));
            this.saveItems(cart);
            this.updateUI();
        }

        return cart;
    }

    /**
     * Clear cart
     */
    static clear() {
        Storage.remove(Cart.STORAGE_KEY);
        this.updateUI();
    }

    /**
     * Get cart total
     * @returns {number} Total price
     */
    static getTotal() {
        const cart = this.getItems();
        return cart.reduce((total, item) => total + (item.precio * item.cantidad), 0);
    }

    /**
     * Get cart item count
     * @returns {number} Total items
     */
    static getItemCount() {
        const cart = this.getItems();
        return cart.reduce((total, item) => total + item.cantidad, 0);
    }

    /**
     * Update cart UI (badge, etc.)
     */
    static updateUI() {
        const count = this.getItemCount();
        const cartCount = document.getElementById('cart-count');

        if (cartCount) {
            cartCount.textContent = count;
            cartCount.style.display = count > 0 ? 'inline-block' : 'none';
        }

        // Trigger custom event for other components
        window.dispatchEvent(new CustomEvent('cartUpdated', {
            detail: { count, total: this.getTotal() }
        }));
    }

    /**
     * Animate cart icon
     */
    static animateIcon() {
        const cartIcon = document.getElementById('cart-icon');
        if (cartIcon) {
            cartIcon.classList.add('cart-animate');
            setTimeout(() => cartIcon.classList.remove('cart-animate'), 300);
        }
    }

    /**
     * Save cart to backend
     * @returns {Promise<Object>} API response
     */
    static async saveToBackend() {
        const cart = this.getItems();
        const total = this.getTotal();

        const cartData = {
            productos: cart,
            total: total
        };

        return await API.post('/api/cart', cartData);
    }

    /**
     * Load cart page content
     */
    static renderCartPage() {
        const cart = this.getItems();
        const container = document.getElementById('cart-items');

        if (!container) return;

        if (cart.length === 0) {
            container.innerHTML = `
                <div class="text-center p-5">
                    <i class="fas fa-shopping-cart fa-3x text-muted mb-3"></i>
                    <h3>Tu carrito está vacío</h3>
                    <p class="text-muted">Agrega productos para comenzar</p>
                    <a href="/api/products" class="btn btn-primary">Ver Productos</a>
                </div>
            `;
            return;
        }

        let html = '';
        cart.forEach(item => {
            html += `
                <div class="cart-item card mb-3" data-id="${item.id}">
                    <div class="card-body">
                        <div class="row align-items-center">
                            <div class="col-md-2">
                                <img src="${item.imagen}" alt="${item.nombre}" class="img-fluid rounded">
                            </div>
                            <div class="col-md-4">
                                <h5 class="card-title">${item.nombre}</h5>
                                <p class="text-muted">${item.mililitros}ml</p>
                            </div>
                            <div class="col-md-2">
                                <input type="number" 
                                       class="form-control quantity-input" 
                                       value="${item.cantidad}" 
                                       min="1"
                                       data-id="${item.id}">
                            </div>
                            <div class="col-md-2">
                                <strong>$${(item.precio * item.cantidad).toFixed(2)}</strong>
                            </div>
                            <div class="col-md-2">
                                <button class="btn btn-danger btn-sm remove-item" data-id="${item.id}">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        html += `
            <div class="cart-total card">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-8 text-end">
                            <h4>Total:</h4>
                        </div>
                        <div class="col-md-4">
                            <h4>$${this.getTotal().toFixed(2)}</h4>
                        </div>
                    </div>
                    <button id="confirmar-productos" class="btn btn-primary btn-block mt-3">
                        Confirmar Pedido
                    </button>
                </div>
            </div>
        `;

        container.innerHTML = html;

        // Attach event listeners
        this.attachCartEventListeners();
    }

    /**
     * Attach event listeners to cart page elements
     */
    static attachCartEventListeners() {
        // Quantity change
        document.querySelectorAll('.quantity-input').forEach(input => {
            input.addEventListener('change', (e) => {
                const id = e.target.dataset.id;
                const quantity = e.target.value;
                this.updateQuantity(id, quantity);
                this.renderCartPage();
            });
        });

        // Remove item
        document.querySelectorAll('.remove-item').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const id = e.target.closest('.remove-item').dataset.id;
                const confirmed = await Notify.confirm('¿Eliminar este producto del carrito?');
                if (confirmed) {
                    this.removeItem(id);
                    this.renderCartPage();
                    Notify.toast('Producto eliminado', 'success');
                }
            });
        });

        // Confirm order
        const confirmBtn = document.getElementById('confirmar-productos');
        if (confirmBtn) {
            confirmBtn.addEventListener('click', async () => {
                try {
                    Notify.loading('Guardando carrito...');
                    const result = await this.saveToBackend();
                    Notify.close();
                    Notify.success('Carrito guardado exitosamente');
                    // Redirect to checkout
                    setTimeout(() => {
                        window.location.href = '/checkOut';
                    }, 1500);
                } catch (error) {
                    Notify.error(error.message || 'Error al guardar el carrito');
                }
            });
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    Cart.updateUI();

    // If on cart page, render it
    if (document.getElementById('cart-items')) {
        Cart.renderCartPage();
    }
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Cart;
}
