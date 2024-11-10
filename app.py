from flask import Flask, request, jsonify, render_template, redirect, url_for
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configuration de la base de données MySQL
db = pymysql.connect(
    host="localhost",
    user="manalalm",  # Remplacez par votre nom d'utilisateur
    password="manal",  # Remplacez par votre mot de passe
    database="docker"  # Remplacez par le nom de votre base de données
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return jsonify({"message": "Username and password are required"}), 400

        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({"message": "Username already taken"}), 400

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        db.commit()
        cursor.close()
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if not user or not check_password_hash(user[2], password):  # user[2] corresponds to the password
            return jsonify({"message": "Incorrect username or password"}), 401

        return redirect(url_for('show_products'))  # Redirection vers la page des produits

    return render_template('login.html')

@app.route('/products')
def show_products():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    return render_template('products.html', products=products)

@app.route('/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    cursor = db.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image_url = request.form['image_url']

        # Mettre à jour le produit dans la base de données
        cursor.execute("""
            UPDATE products 
            SET name = %s, description = %s, price = %s, image_url = %s 
            WHERE id = %s
        """, (name, description, price, image_url, product_id))
        db.commit()
        cursor.close()
        return redirect(url_for('show_products'))

    # Récupérer les informations du produit à modifier
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    
    # Vérifiez si le produit existe
    if product is None:
        return "Produit non trouvé", 404
    
    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
    db.commit()
    cursor.close()
    return redirect(url_for('show_products'))
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        # Récupération des données du formulaire
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image_url = request.form['image_url']

        try:
            cursor = db.cursor()
            # Exécution de la requête d'insertion
            cursor.execute("INSERT INTO products (name, description, price, image_url) VALUES (%s, %s, %s, %s)", 
                           (name, description, price, image_url))
            db.commit()  # Sauvegarde les modifications dans la base de données
            cursor.close()

            return redirect(url_for('add_product'))  # Redirection vers le formulaire d'ajout
        except Exception as e:
            db.rollback()  # Annule si une erreur se produit
            print(f"Erreur lors de l'ajout du produit : {e}")
            cursor.close()



    return render_template('add.html')
if __name__ == '__main__':
    app.run(debug=True)
