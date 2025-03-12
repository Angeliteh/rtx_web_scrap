# database.py
import sqlite3
import psycopg2
import pymongo
from datetime import datetime
from src.config.config import DATABASE_TYPE, DATABASE_NAME, POSTGRES_CONFIG, MONGODB_CONFIG, PALABRAS_PROHIBIDAS
import os

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
        tuple: (historial, info_producto)
            - historial: Lista de diccionarios con fecha y precio
            - info_producto: Diccionario con información del producto o None si no existe
    """
    try:
        # Verificar si la base de datos existe
        if DATABASE_TYPE != "mongodb" and not os.path.exists(DATABASE_NAME):
            print(f"Base de datos no encontrada: {DATABASE_NAME}")
            return [], None
            
        conn, db_type = get_db_connection()
        historial = []
        info_producto = None
        
        try:
            if db_type == "mongodb":
                # MongoDB
                productos_collection = conn[MONGODB_CONFIG['collection']]
                historial_collection = conn['historial_precios']
                
                # Obtener información del producto
                producto = productos_collection.find_one({"id_producto": id_producto})
                if not producto:
                    return [], None
                    
                info_producto = {
                    "nombre": producto.get("nombre", ""),
                    "modelo": producto.get("modelo", ""),
                    "tienda": producto.get("tienda", ""),
                    "vendedor": producto.get("vendedor", ""),
                    "link": producto.get("link", ""),
                    "imagen": producto.get("imagen", "")
                }
                
                # Obtener historial ordenado por fecha
                historial_cursor = historial_collection.find(
                    {"id_producto": id_producto}
                ).sort("fecha", -1).limit(limite)
                
                historial = [{
                    "fecha": registro["fecha"],
                    "precio": registro["precio"],
                    "vendedor": registro.get("vendedor", "")
                } for registro in historial_cursor]
                
            else:
                # SQLite o PostgreSQL
                cursor = conn.cursor()
                
                # Verificar si la tabla productos existe
                try:
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='productos'")
                    if not cursor.fetchone():
                        print("La tabla 'productos' no existe en la base de datos")
                        return [], None
                except Exception as e:
                    print(f"Error verificando tablas: {e}")
                    # Continuar de todos modos, por si es PostgreSQL
                
                # Obtener información del producto
                try:
                    cursor.execute("""
                        SELECT nombre, modelo, tienda, vendedor, link, imagen
                        FROM productos
                        WHERE id_producto = ?
                    """, (id_producto,))
                    
                    producto = cursor.fetchone()
                    if not producto:
                        return [], None
                        
                    info_producto = {
                        "nombre": producto[0] if producto[0] else "",
                        "modelo": producto[1] if producto[1] else "",
                        "tienda": producto[2] if producto[2] else "",
                        "vendedor": producto[3] if producto[3] else "",
                        "link": producto[4] if producto[4] else "",
                        "imagen": producto[5] if producto[5] else ""
                    }
                except Exception as e:
                    print(f"Error obteniendo información del producto: {e}")
                    return [], None
                
                # Obtener historial
                try:
                    cursor.execute("""
                        SELECT hp.fecha, hp.precio, hp.vendedor
                        FROM historial_precios hp
                        JOIN productos p ON hp.producto_id = p.id
                        WHERE p.id_producto = ?
                        ORDER BY hp.fecha DESC
                        LIMIT ?
                    """, (id_producto, limite))
                    
                    historial = [{
                        "fecha": registro[0] if registro[0] else "",
                        "precio": registro[1] if registro[1] else 0,
                        "vendedor": registro[2] if registro[2] else ""
                    } for registro in cursor.fetchall()]
                except Exception as e:
                    print(f"Error obteniendo historial: {e}")
                    # Si hay error en el historial pero tenemos info del producto,
                    # devolver producto con historial vacío
                    if info_producto:
                        return [], info_producto
                    return [], None
                
            return historial, info_producto
            
        except Exception as e:
            print(f"Error en la consulta a la base de datos: {e}")
            return [], None
            
    except Exception as e:
        print(f"Error general obteniendo historial de precios: {e}")
        return [], None
        
    finally:
        if 'conn' in locals() and db_type != "mongodb":
            try:
                conn.close()
            except Exception:
                pass

def contiene_palabra_prohibida(nombre):
    """
    Verifica si un nombre de producto contiene alguna palabra prohibida.
    
    Args:
        nombre (str): Nombre del producto a verificar
        
    Returns:
        bool: True si contiene alguna palabra prohibida, False en caso contrario
    """
    nombre_lower = nombre.lower()
    return any(palabra.lower() in nombre_lower for palabra in PALABRAS_PROHIBIDAS)

def limpiar_productos_prohibidos():
    """
    Elimina de la base de datos los productos que contienen palabras prohibidas.
    """
    conn, db_type = get_db_connection()
    
    try:
        if db_type == "mongodb":
            productos_collection = conn[MONGODB_CONFIG['collection']]
            productos = productos_collection.find({})
            
            for producto in productos:
                if contiene_palabra_prohibida(producto["nombre"]):
                    productos_collection.delete_one({"_id": producto["_id"]})
                    
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM productos")
            productos = cursor.fetchall()
            
            for producto_id, nombre in productos:
                if contiene_palabra_prohibida(nombre):
                    cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
                    cursor.execute("DELETE FROM historial_precios WHERE producto_id = ?", (producto_id,))
            
            conn.commit()
            
    finally:
        if db_type != "mongodb":
            conn.close()

def obtener_todos_productos(filtros=None, ordenar_por='precio', orden='ASC'):
    """
    Obtiene todos los productos de la base de datos, excluyendo aquellos con palabras prohibidas.
    
    Args:
        filtros (dict, opcional): Filtros a aplicar (ej: {"modelo": "RTX 4070"})
        ordenar_por (str): Campo por el cual ordenar los resultados
        orden (str): Dirección del ordenamiento ('ASC' o 'DESC')
        
    Returns:
        list: Lista de diccionarios con información de productos
    """
    conn, db_type = get_db_connection()
    productos = []
    
    if db_type == "mongodb":
        productos_collection = conn[MONGODB_CONFIG['collection']]
        
        query = {}
        if filtros:
            for clave, valor in filtros.items():
                if valor:
                    if clave == 'tienda':
                        query[clave] = {'$regex': f'^{valor}$', '$options': 'i'}
                    elif clave == 'modelo':
                        query[clave] = {'$regex': valor, '$options': 'i'}
        
        sort_direction = pymongo.ASCENDING if orden == 'ASC' else pymongo.DESCENDING
        cursor = productos_collection.find(query).sort(ordenar_por, sort_direction)
        
        for producto in cursor:
            if not contiene_palabra_prohibida(producto["nombre"]):
                if "_id" in producto:
                    del producto["_id"]
                productos.append(producto)
    else:
        cursor = conn.cursor()
        
        query = "SELECT tienda, modelo, nombre, precio, fecha, vendedor, link, imagen, id_producto FROM productos"
        params = []
        
        if filtros:
            condiciones = []
            for clave, valor in filtros.items():
                if valor:
                    if clave == 'tienda':
                        condiciones.append("LOWER(tienda) = LOWER(?)")
                        params.append(valor)
                    elif clave == 'modelo':
                        condiciones.append("modelo LIKE ?")
                        params.append(f"%{valor}%")
            
            if condiciones:
                query += " WHERE " + " AND ".join(condiciones)
        
        query += f" ORDER BY {ordenar_por} {orden}"
        
        cursor.execute(query, params)
        
        for row in cursor.fetchall():
            if not contiene_palabra_prohibida(row[2]):  # row[2] es el nombre del producto
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
    
    if db_type != "mongodb":
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

def obtener_productos_actuales(limite=100):
    """
    Obtiene los productos actuales de la base de datos.
    
    Args:
        limite (int): Número máximo de productos a devolver
        
    Returns:
        list: Lista de diccionarios con información de productos
    """
    conn, db_type = get_db_connection()
    productos = []
    
    try:
        if db_type == "mongodb":
            # MongoDB
            collection = conn[MONGODB_CONFIG['collection']]
            cursor = collection.find().sort("fecha", -1).limit(limite)
            productos = list(cursor)
            
        else:
            # SQLite o PostgreSQL
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, tienda, modelo, nombre, precio, fecha, vendedor, link, imagen, id_producto
                FROM productos
                ORDER BY fecha DESC
                LIMIT ?
            ''', (limite,))
            
            columnas = ['id', 'tienda', 'modelo', 'nombre', 'precio', 'fecha', 'vendedor', 'link', 'imagen', 'id_producto']
            productos = [dict(zip(columnas, row)) for row in cursor.fetchall()]
            
    except Exception as e:
        print(f"Error al obtener productos actuales: {e}")
        
    finally:
        if db_type != "mongodb":
            conn.close()
            
    return productos
