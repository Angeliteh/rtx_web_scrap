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
            imagen TEXT,
            asin TEXT
        )
    ''')
    conn.commit()
    conn.close()

def guardar_en_db(productos):
    """
    Guarda productos en la base de datos, evitando duplicados.
    Si un producto ya existe, actualiza su precio en lugar de insertarlo de nuevo.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    for producto in productos:
        # Verificar si el producto ya está en la base de datos (basado en su asin)
        c.execute("SELECT id FROM productos WHERE asin = ?", (producto["asin"],))
        existente = c.fetchone()
        
        if existente:
            # Si ya existe, actualizar el precio en lugar de insertarlo de nuevo
            c.execute("UPDATE productos SET precio = ?, fecha = ? WHERE id = ?", 
                    (producto["precio"], datetime.now().isoformat(), existente[0]))
        else:
            # Si no existe, insertarlo normalmente
            c.execute('''
                INSERT INTO productos (tienda, modelo, nombre, precio, fecha, vendedor, link, imagen, asin)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                producto["tienda"], producto["modelo"], producto["nombre"],
                producto["precio"], datetime.now().isoformat(),
                producto["vendedor"], producto["link"], producto["imagen"],
                producto["asin"]
            ))

    conn.commit()
    conn.close()
