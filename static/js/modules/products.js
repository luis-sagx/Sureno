/**
 * Products Module - Product display and interaction
 */

class Products {
    /**
     * Add product to cart with notification
     * @param {Object} product - Product data
     */
    static addToCart(product) {
        Cart.addItem(product);
        Cart.animateIcon();
        Notify.success(`"${product.nombre}" agregado al carrito`);
    }

    /**
     * Initialize product cards
     */
    static initProductCards() {
        document.querySelectorAll('.add-to-cart-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();

                const productData = {
                    id: button.dataset.id,
                    nombre: button.dataset.nombre,
                    precio: button.dataset.precio,
                    imagen: button.dataset.imagen,
                    mililitros: button.dataset.mililitros
                };

                this.addToCart(productData);
            });
        });
    }

    /**
     * Initialize product filter
     */
    static initProductFilter() {
        const filterButtons = document.querySelectorAll('[data-filter]');
        const productCards = document.querySelectorAll('[data-category]');

        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                const filter = button.dataset.filter;

                // Update active button
                filterButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');

                // Filter products
                productCards.forEach(card => {
                    if (filter === 'all' || card.dataset.category === filter) {
                        card.style.display = 'block';
                        card.classList.add('fade-in');
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        });
    }

    /**
     * Initialize product search
     */
    static initProductSearch() {
        const searchInput = document.getElementById('product-search');
        if (!searchInput) return;

        const productCards = document.querySelectorAll('[data-nombre]');

        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();

            productCards.forEach(card => {
                const productName = card.dataset.nombre.toLowerCase();
                if (productName.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    Products.initProductCards();
    Products.initProductFilter();
    Products.initProductSearch();
});

// Global function for inline onclick (backward compatibility)
function agregarAlCarrito(id, nombre, precio, imagen, mililitros) {
    Products.addToCart({ id, nombre, precio, imagen, mililitros });
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Products;
}
