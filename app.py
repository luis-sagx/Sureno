from flask import Flask, render_template
from routes import register_routes

app = Flask(__name__)

@app.route('/')
def confirmacion():
    return render_template('confirmacion.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('aboutUs.html')

from models.product import ProductModel

@app.route('/products')
def products():
    products = ProductModel.get_all()
    for product in products:
        product['_id'] = str(product['_id'])
    return render_template('product.html', products=products)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/login')
def login():
    return render_template('login.html')

register_routes(app)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
