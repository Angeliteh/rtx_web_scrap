# app.py
from flask import Flask, render_template
import sqlite3
from config import DATABASE_NAME
from main import ejecutar_scraper  # Importamos la función para hacer scraping
from database import crear_tabla

app = Flask(__name__)

# Crear la tabla al iniciar Flask (por si no existe)
crear_tabla()

def obtener_productos():
    """
    Obtiene los productos almacenados en la base de datos.
    Si la base de datos está vacía, ejecuta automáticamente el scraper.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    # Verificar si hay productos en la base de datos
    c.execute("SELECT COUNT(*) FROM productos")
    cantidad_productos = c.fetchone()[0]

    if cantidad_productos == 0:
        print("⚠️ No hay productos en la base de datos. Ejecutando el scraper...")
        ejecutar_scraper()  # Llamamos al scraper automáticamente

    # Ahora obtenemos los productos
    c.execute("SELECT nombre, precio, link, imagen FROM productos ORDER BY precio ASC")
    productos = c.fetchall()
    
    conn.close()
    return productos

@app.route('/')
def index():
    """
    Página principal que muestra los productos en una tabla.
    """
    productos = obtener_productos()
    return render_template('index.html', productos=productos)

if __name__ == '__main__':
    app.run(debug=True)
