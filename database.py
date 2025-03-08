# database.py
import sqlite3
import psycopg2
import pymongo
from datetime import datetime
from config import DATABASE_TYPE, DATABASE_NAME, POSTGRES_CONFIG, MONGODB_CONFIG

def get_db_connection():
    """
    Obtiene una conexión a la base de datos según el tipo configurado.
    
    Returns:
        tuple: (conexión, tipo_db)
    """
    if DATABASE_TYPE == "postgresql":
        # Conexión a PostgreSQL
        conn = psycopg2.connect(
            host=POSTGRES_CONFIG['host'],
            port=POSTGRES_CONFIG['port'],
            database=POSTGRES_CONFIG['database'],
            user=POSTGRES_CONFIG['user'],
            password=POSTGRES_CONFIG['password']
        )
        return conn, "postgresql"
    elif DATABASE_TYPE == "mongodb":
        # Conexión a MongoDB
        client = pymongo.MongoClient(
            host=MONGODB_CONFIG['host'],
            port=MONGODB_CONFIG['port']
        )
        db = client[MONGODB_CONFIG['database']]
        return db, "mongodb"
    else:
        # Por defecto, SQLite
        conn = sqlite3.connect(DATABASE_NAME)
        return conn, "sqlite"

def crear_tabla():
    """
    Crea las tablas necesarias según el tipo de base de datos configurado.
    
    Para SQLite y PostgreSQL:
      - tabla 'productos': almacena la información actual de cada producto
      - tabla 'historial_precios': almacena el historial de precios de cada producto
      
    Para MongoDB, se crean las colecciones equivalentes.
    """
    conn, db_type = get_db_connection()
    
    if db_type == "mongodb":
        # En MongoDB no es necesario crear esquemas previamente
        # pero podemos crear índices para optimizar consultas
        productos_collection = conn[MONGODB_CONFIG['collection']]
        historial_collection = conn['historial_precios']
        
        # Crear índices
        productos_collection.create_index([("id_producto", pymongo.ASCENDING)], unique=True)
        historial_collection.create_index([
            ("id_producto", pymongo.ASCENDING),
            ("fecha", pymongo.DESCENDING)
        ])
    else:
        # SQLite o PostgreSQL
        cursor = conn.cursor()
        
        # Tabla de productos (información actual)
        if db_type == "postgresql":
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS productos (
                    id SERIAL PRIMARY KEY,
                    tienda TEXT,
                    modelo TEXT,
                    nombre TEXT,
                    precio REAL,
                    fecha TIMESTAMP,
                    vendedor TEXT,
                    link TEXT,
                    imagen TEXT,
                    id_producto TEXT UNIQUE
                )
            ''')
            
            # Tabla de historial de precios
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historial_precios (
                    id SERIAL PRIMARY KEY,
                    producto_id INTEGER REFERENCES productos(id),
                    precio REAL,
                    fecha TIMESTAMP,
                    vendedor TEXT
                )
            ''')
        else:  # SQLite
            cursor.execute('''
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
                    id_producto TEXT UNIQUE
                )
            ''')
            
            # Tabla de historial de precios
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historial_precios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    producto_id INTEGER,
                    precio REAL,
                    fecha TEXT,
                    vendedor TEXT,
                    FOREIGN KEY (producto_id) REFERENCES productos(id)
                )
            ''')
        
        conn.commit()
        
    # Cerrar conexión
    if db_type != "mongodb":
        conn.close()

def guardar_en_db(productos):
    """
    Guarda productos en la base de datos, evitando duplicados.
    Si un producto ya existe:
      - Actualiza su información en la tabla 'productos'
      - Añade un nuevo registro en la tabla 'historial_precios'
    
    Args:
        productos (list): Lista de diccionarios con información de productos
    """
    conn, db_type = get_db_connection()
    fecha_actual = datetime.now()
    
    if db_type == "mongodb":
        # MongoDB
        productos_collection = conn[MONGODB_CONFIG['collection']]
        historial_collection = conn['historial_precios']
        
        for producto in productos:
            # Verificar si el producto ya existe
            producto_existente = productos_collection.find_one({"id_producto": producto["id_producto"]})
            
            # Preparar datos para historial
            historial = {
                "id_producto": producto["id_producto"],
                "precio": producto["precio"],
                "fecha": fecha_actual,
                "vendedor": producto["vendedor"]
            }
            
            if producto_existente:
                # Si el precio ha cambiado, actualizar y guardar historial
                if producto_existente["precio"] != producto["precio"]:
                    # Actualizar producto
                    productos_collection.update_one(
                        {"id_producto": producto["id_producto"]},
                        {"$set": {
                            "precio": producto["precio"],
                            "fecha": fecha_actual,
                            "vendedor": producto["vendedor"]
                        }}
                    )
                    
                    # Guardar en historial
                    historial_collection.insert_one(historial)
            else:
                # Insertar nuevo producto
                producto["fecha"] = fecha_actual
                productos_collection.insert_one(producto)
                
                # Guardar primer registro en historial
                historial_collection.insert_one(historial)
    else:
        # SQLite o PostgreSQL
        cursor = conn.cursor()
        fecha_str = fecha_actual.isoformat()
        
        for producto in productos:
            # Verificar si el producto ya existe
            cursor.execute("SELECT id, precio FROM productos WHERE id_producto = ?", (producto["id_producto"],))
            existente = cursor.fetchone()
            
            if existente:
                producto_id, precio_actual = existente
                
                # Si el precio ha cambiado, actualizar y guardar historial
                if precio_actual != producto["precio"]:
                    # Actualizar producto
                    cursor.execute(
                        "UPDATE productos SET precio = ?, fecha = ?, vendedor = ? WHERE id = ?", 
                        (producto["precio"], fecha_str, producto["vendedor"], producto_id)
                    )
                    
                    # Guardar en historial
                    cursor.execute(
                        "INSERT INTO historial_precios (producto_id, precio, fecha, vendedor) VALUES (?, ?, ?, ?)",
                        (producto_id, producto["precio"], fecha_str, producto["vendedor"])
                    )
            else:
                # Insertar nuevo producto
                cursor.execute('''
                    INSERT INTO productos (tienda, modelo, nombre, precio, fecha, vendedor, link, imagen, id_producto)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    producto["tienda"], producto["modelo"], producto["nombre"],
                    producto["precio"], fecha_str, producto["vendedor"], 
                    producto["link"], producto["imagen"], producto["id_producto"]
                ))
                
                # Obtener el ID del producto recién insertado
                if db_type == "postgresql":
                    cursor.execute("SELECT lastval()")
                    producto_id = cursor.fetchone()[0]
                else:  # SQLite
                    producto_id = cursor.lastrowid
                
                # Guardar primer registro en historial
                cursor.execute(
                    "INSERT INTO historial_precios (producto_id, precio, fecha, vendedor) VALUES (?, ?, ?, ?)",
                    (producto_id, producto["precio"], fecha_str, producto["vendedor"])
                )
        
        conn.commit()
    
    # Cerrar conexión
    if db_type != "mongodb":
        conn.close()

def obtener_historial_precios(id_producto, limite=30):
    """
    Obtiene el historial de precios de un producto específico.
    
    Args:
        id_producto (str): Identificador único del producto
        limite (int): Número máximo de registros a devolver
        
    Returns:
        list: Lista de diccionarios con fecha y precio
    """
    conn, db_type = get_db_connection()
    historial = []
    
    if db_type == "mongodb":
        # MongoDB
        historial_collection = conn['historial_precios']
        
        # Consultar historial
        registros = historial_collection.find(
            {"id_producto": id_producto}
        ).sort("fecha", -1).limit(limite)
        
        for registro in registros:
            historial.append({
                "fecha": registro["fecha"],
                "precio": registro["precio"],
                "vendedor": registro.get("vendedor", "")
            })
    else:
        # SQLite o PostgreSQL
        cursor = conn.cursor()
        
        # Consultar historial
        cursor.execute('''
            SELECT h.fecha, h.precio, h.vendedor 
            FROM historial_precios h
            JOIN productos p ON h.producto_id = p.id
            WHERE p.id_producto = ?
            ORDER BY h.fecha DESC
            LIMIT ?
        ''', (id_producto, limite))
        
        registros = cursor.fetchall()
        
        for registro in registros:
            historial.append({
                "fecha": registro[0],
                "precio": registro[1],
                "vendedor": registro[2] if registro[2] else ""
            })
        
        conn.close()
    
    return historial

def obtener_todos_productos(filtros=None):
    """
    Obtiene todos los productos de la base de datos.
    
    Args:
        filtros (dict, opcional): Filtros a aplicar (ej: {"modelo": "RTX 4070"})
        
    Returns:
        list: Lista de diccionarios con información de productos
    """
    conn, db_type = get_db_connection()
    productos = []
    
    if db_type == "mongodb":
        # MongoDB
        productos_collection = conn[MONGODB_CONFIG['collection']]
        
        # Aplicar filtros si existen
        query = {}
        if filtros:
            for clave, valor in filtros.items():
                query[clave] = valor
        
        # Consultar productos
        cursor = productos_collection.find(query)
        
        for producto in cursor:
            # Eliminar el campo _id generado por MongoDB (no es serializable)
            if "_id" in producto:
                del producto["_id"]
            productos.append(producto)
    else:
        # SQLite o PostgreSQL
        cursor = conn.cursor()
        
        # Construir la consulta según los filtros
        query = "SELECT tienda, modelo, nombre, precio, fecha, vendedor, link, imagen, id_producto FROM productos"
        params = []
        
        if filtros:
            condiciones = []
            for clave, valor in filtros.items():
                condiciones.append(f"{clave} = ?")
                params.append(valor)
            
            if condiciones:
                query += " WHERE " + " AND ".join(condiciones)
        
        # Ejecutar consulta
        cursor.execute(query, params)
        
        for row in cursor.fetchall():
            productos.append({
                "tienda": row[0],
                "modelo": row[1],
                "nombre": row[2],
                "precio": row[3],
                "fecha": row[4],
                "vendedor": row[5],
                "link": row[6],
                "imagen": row[7],
                "id_producto": row[8]
            })
        
        conn.close()
    
    return productos

def obtener_estadisticas():
    """
    Obtiene estadísticas generales sobre los productos.
    
    Returns:
        dict: Diccionario con estadísticas
    """
    conn, db_type = get_db_connection()
    estadisticas = {
        "total_productos": 0,
        "por_tienda": {},
        "por_modelo": {},
        "precio_promedio": {},
        "precio_minimo": {},
        "precio_maximo": {}
    }
    
    if db_type == "mongodb":
        # MongoDB
        productos_collection = conn[MONGODB_CONFIG['collection']]
        
        # Total de productos
        estadisticas["total_productos"] = productos_collection.count_documents({})
        
        # Por tienda
        tiendas = productos_collection.distinct("tienda")
        for tienda in tiendas:
            estadisticas["por_tienda"][tienda] = productos_collection.count_documents({"tienda": tienda})
        
        # Por modelo
        modelos = productos_collection.distinct("modelo")
        for modelo in modelos:
            estadisticas["por_modelo"][modelo] = productos_collection.count_documents({"modelo": modelo})
            
            # Calcular precios para cada modelo
            productos_modelo = productos_collection.find({"modelo": modelo})
            precios = [p["precio"] for p in productos_modelo if p["precio"] > 0]
            
            if precios:
                estadisticas["precio_promedio"][modelo] = sum(precios) / len(precios)
                estadisticas["precio_minimo"][modelo] = min(precios)
                estadisticas["precio_maximo"][modelo] = max(precios)
    else:
        # SQLite o PostgreSQL
        cursor = conn.cursor()
        
        # Total de productos
        cursor.execute("SELECT COUNT(*) FROM productos")
        estadisticas["total_productos"] = cursor.fetchone()[0]
        
        # Por tienda
        cursor.execute("SELECT tienda, COUNT(*) FROM productos GROUP BY tienda")
        for tienda, cantidad in cursor.fetchall():
            estadisticas["por_tienda"][tienda] = cantidad
        
        # Por modelo
        cursor.execute("SELECT modelo, COUNT(*) FROM productos GROUP BY modelo")
        for modelo, cantidad in cursor.fetchall():
            estadisticas["por_modelo"][modelo] = cantidad
            
            # Calcular precios para cada modelo
            cursor.execute("SELECT AVG(precio), MIN(precio), MAX(precio) FROM productos WHERE modelo = ? AND precio > 0", (modelo,))
            promedio, minimo, maximo = cursor.fetchone()
            
            if promedio is not None:
                estadisticas["precio_promedio"][modelo] = promedio
                estadisticas["precio_minimo"][modelo] = minimo
                estadisticas["precio_maximo"][modelo] = maximo
        
        conn.close()
    
    return estadisticas
