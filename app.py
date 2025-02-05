from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('aboutUs.html')

@app.route('/products')
def products():
    return render_template('product.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/cart')
def cart():
    return "Página del carrito"

@app.route('/login')
def login():
    return "Página de login"

if __name__ == '__main__':
    app.run(debug=True)
