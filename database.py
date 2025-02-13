# database.py
import sqlite3
from datetime import datetime
from config import DATABASE_NAME

def crear_tabla():
    """
    Crea la tabla 'productos' si no existe.
    Se incluyen campos para:
      - tienda, modelo, nombre, precio, fecha, vendedor, link e imagen.
    Esto permite almacenar productos de distintos marketplaces en una única tabla.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tienda TEXT,
            modelo TEXT,
            nombre TEXT,
            precio REAL,
            fecha TEXT,
            vendedor TEXT,
            link TEXT,
            imagen TEXT
        )
    ''')
    conn.commit()
    conn.close()

def guardar_en_db(productos):
    """
    Guarda en la base de datos una lista de productos.
    Cada producto es un diccionario con la información extraída.
    Se convierte la fecha a string (ISO 8601) para compatibilidad con Python 3.12+.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    for producto in productos:
        c.execute('''
            INSERT INTO productos (tienda, modelo, nombre, precio, fecha, vendedor, link, imagen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            producto.get('tienda', 'Amazon'),
            producto['modelo'],
            producto['nombre'],
            producto['precio'],
            datetime.now().isoformat(),
            producto.get('vendedor', ''),
            producto.get('link', ''),
            producto.get('imagen', '')
        ))
    
    conn.commit()
    conn.close()
