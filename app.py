# app.py
from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime, timedelta
from config import DATABASE_NAME, SITIOS_HABILITADOS, MODELOS_BUSQUEDA
from main import ejecutar_scraper
from database import crear_tabla, get_db_connection, obtener_historial_precios

app = Flask(__name__)

# Crear la tabla al iniciar Flask (por si no existe)
crear_tabla()

def obtener_productos(tienda=None, modelo=None, ordenar_por="precio", orden="ASC", limite=100):
    """
    Obtiene los productos almacenados en la base de datos con opciones de filtrado.
    
    Args:
        tienda (str, opcional): Filtrar por tienda específica
        modelo (str, opcional): Filtrar por modelo específico
        ordenar_por (str): Campo por el que ordenar (precio, nombre, fecha)
        orden (str): Orden ascendente (ASC) o descendente (DESC)
        limite (int): Número máximo de productos a devolver
        
    Returns:
        list: Lista de productos
    """
    conn, db_type = get_db_connection()
    
    if db_type == "mongodb":
        # MongoDB
        collection = conn['productos']
        
        # Construir filtro
        filtro = {}
        if tienda:
            filtro["tienda"] = tienda
        if modelo:
            filtro["modelo"] = modelo
            
        # Ordenar
        orden_valor = 1 if orden == "ASC" else -1
        ordenacion = [(ordenar_por, orden_valor)]
        
        # Ejecutar consulta
        cursor = collection.find(filtro).sort(ordenacion).limit(limite)
        productos = list(cursor)
        
    else:
        # SQLite o PostgreSQL
        cursor = conn.cursor()
        
        # Construir consulta SQL base
        query = """
            SELECT id, tienda, modelo, nombre, precio, fecha, vendedor, link, imagen, id_producto 
            FROM productos 
            WHERE 1=1
        """
        params = []
        
        # Añadir filtros si existen
        if tienda:
            query += " AND tienda = ?"
            params.append(tienda)
        if modelo:
            query += " AND modelo = ?"
            params.append(modelo)
            
        # Añadir ordenación
        query += f" ORDER BY {ordenar_por} {orden}"
        
        # Añadir límite
        query += " LIMIT ?"
        params.append(limite)
        
        # Verificar si hay productos en la base de datos
        cursor.execute("SELECT COUNT(*) FROM productos")
        cantidad_productos = cursor.fetchone()[0]

        if cantidad_productos == 0:
            print("⚠️ No hay productos en la base de datos. Ejecutando el scraper...")
            ejecutar_scraper()  # Llamamos al scraper automáticamente
            
            # Volver a ejecutar la consulta después del scraping
            cursor.execute(query, params)
        else:
            # Ejecutar la consulta con los parámetros
            cursor.execute(query, params)
            
        # Obtener resultados
        productos = []
        for row in cursor.fetchall():
            productos.append({
                'id': row[0],
                'tienda': row[1],
                'modelo': row[2],
                'nombre': row[3],
                'precio': row[4],
                'fecha': row[5],
                'vendedor': row[6],
                'link': row[7],
                'imagen': row[8],
                'id_producto': row[9]
            })
        
        # Cerrar conexión
        conn.close()
        
    return productos

def obtener_estadisticas():
    """
    Obtiene estadísticas generales sobre los productos.
    
    Returns:
        dict: Diccionario con estadísticas
    """
    conn, db_type = get_db_connection()
    
    if db_type == "mongodb":
        # MongoDB
        collection = conn['productos']
        
        # Obtener tiendas únicas
        tiendas = collection.distinct("tienda")
        
        # Obtener modelos únicos
        modelos = collection.distinct("modelo")
        
        # Obtener precio mínimo, máximo y promedio
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "min_precio": {"$min": "$precio"},
                    "max_precio": {"$max": "$precio"},
                    "avg_precio": {"$avg": "$precio"},
                    "total": {"$sum": 1}
                }
            }
        ]
        
        resultado = list(collection.aggregate(pipeline))
        if resultado:
            stats = resultado[0]
            min_precio = stats["min_precio"]
            max_precio = stats["max_precio"]
            avg_precio = stats["avg_precio"]
            total_productos = stats["total"]
        else:
            min_precio = max_precio = avg_precio = 0
            total_productos = 0
            
    else:
        # SQLite o PostgreSQL
        cursor = conn.cursor()
        
        # Obtener tiendas únicas
        cursor.execute("SELECT DISTINCT tienda FROM productos")
        tiendas = [row[0] for row in cursor.fetchall()]
        
        # Obtener modelos únicos
        cursor.execute("SELECT DISTINCT modelo FROM productos")
        modelos = [row[0] for row in cursor.fetchall()]
        
        # Obtener precio mínimo, máximo y promedio
        cursor.execute("SELECT MIN(precio), MAX(precio), AVG(precio), COUNT(*) FROM productos")
        min_precio, max_precio, avg_precio, total_productos = cursor.fetchone()
        
        # Cerrar conexión
        conn.close()
    
    return {
        'tiendas': tiendas,
        'modelos': modelos,
        'min_precio': min_precio,
        'max_precio': max_precio,
        'avg_precio': avg_precio,
        'total_productos': total_productos
    }

@app.route('/')
def index():
    """
    Página principal que muestra los productos en una tabla con opciones de filtrado.
    """
    # Obtener parámetros de filtrado
    tienda = request.args.get('tienda')
    modelo = request.args.get('modelo')
    ordenar_por = request.args.get('ordenar_por', 'precio')
    orden = request.args.get('orden', 'ASC')
    
    # Obtener productos filtrados
    productos = obtener_productos(tienda, modelo, ordenar_por, orden)
    
    # Obtener estadísticas
    estadisticas = obtener_estadisticas()
    
    return render_template(
        'index.html', 
        productos=productos, 
        estadisticas=estadisticas,
        tiendas=estadisticas['tiendas'],
        modelos=estadisticas['modelos'],
        filtros={
            'tienda': tienda,
            'modelo': modelo,
            'ordenar_por': ordenar_por,
            'orden': orden
        },
        now=datetime.now()  # Aquí pasamos la variable `now`
    )

@app.route('/historial/<id_producto>')
def historial(id_producto):
    """
    Página que muestra el historial de precios de un producto específico.
    """
    # Obtener el producto
    conn, db_type = get_db_connection()
    
    if db_type == "mongodb":
        # MongoDB
        collection = conn['productos']
        producto = collection.find_one({"id_producto": id_producto})
    else:
        # SQLite o PostgreSQL
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, tienda, modelo, nombre, precio, fecha, vendedor, link, imagen, id_producto FROM productos WHERE id_producto = ?", 
            (id_producto,)
        )
        row = cursor.fetchone()
        
        if row:
            producto = {
                'id': row[0],
                'tienda': row[1],
                'modelo': row[2],
                'nombre': row[3],
                'precio': row[4],
                'fecha': row[5],
                'vendedor': row[6],
                'link': row[7],
                'imagen': row[8],
                'id_producto': row[9]
            }
        else:
            producto = None
            
        # Cerrar conexión
        conn.close()
    
    if not producto:
        return "Producto no encontrado", 404
    
    # Obtener historial de precios
    historial = obtener_historial_precios(id_producto, limite=30)
    
    # Preparar datos para el gráfico
    fechas = []
    precios = []
    
    for registro in historial:
        fechas.append(registro['fecha'])
        precios.append(registro['precio'])
    
    return render_template(
        'historial.html',
        producto=producto,
        historial=historial,
        fechas=fechas,
        precios=precios
    )

@app.route('/api/productos')
def api_productos():
    """
    API para obtener productos en formato JSON.
    """
    # Obtener parámetros de filtrado
    tienda = request.args.get('tienda')
    modelo = request.args.get('modelo')
    ordenar_por = request.args.get('ordenar_por', 'precio')
    orden = request.args.get('orden', 'ASC')
    
    # Obtener productos filtrados
    productos = obtener_productos(tienda, modelo, ordenar_por, orden)
    
    return jsonify(productos)

@app.route('/actualizar')
def actualizar():
    """
    Ejecuta el scraper manualmente y redirige a la página principal.
    """
    ejecutar_scraper()
    return render_template('actualizar.html')

if __name__ == '__main__':
    app.run(debug=True)
