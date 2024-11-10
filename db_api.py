from flask import Flask, render_template, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Configuration de la connexion à la base de données
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'e_commerce'
}

# Route pour afficher les produits
@app.route('/products')
def products():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('products.html', products=products)

# Route pour supprimer un produit
@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('products'))

if __name__ == '__main__':
    app.run(debug=True)
