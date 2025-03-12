# app.py
from flask import Flask, render_template, request, jsonify, abort
from datetime import datetime
from functools import wraps
import logging
import sqlite3
import os

from src.config.config import DATABASE_NAME, SITIOS_HABILITADOS, MODELOS_BUSQUEDA
from src.database.database import (
    crear_tabla,
    get_db_connection,
    obtener_historial_precios,
    obtener_productos_actuales,
    obtener_estadisticas,
    obtener_todos_productos
)
from main import ejecutar_scraper
from src.utils.analysis import generar_grafico_precios
from src.utils.utils import formatear_precio

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicialización de Flask con la ruta correcta de templates
app = Flask(__name__, 
           template_folder='src/templates',
           static_folder='src/static')

# Crear la tabla al iniciar Flask
try:
    crear_tabla()
except Exception as e:
    logger.error(f"Error al crear la tabla: {e}")

def adaptar_estadisticas(stats):
    """
    Adapta las estadísticas devueltas por la función obtener_estadisticas 
    al formato que espera la plantilla.
    """
    # Obtenemos todos los precios
    precios = []
    for modelo, cantidad in stats.get("por_modelo", {}).items():
        # Agregamos los precios de este modelo si existen
        if modelo in stats.get("precio_minimo", {}):
            precios.append(stats["precio_minimo"][modelo])
        if modelo in stats.get("precio_maximo", {}):
            precios.append(stats["precio_maximo"][modelo])
    
    # Calculamos estadísticas globales
    resultado = {
        "total_productos": stats.get("total_productos", 0),
        "min_precio": min(precios) if precios else 0,
        "max_precio": max(precios) if precios else 0,
        "avg_precio": sum(precios) / len(precios) if precios else 0
    }
    
    return resultado

def validar_parametros_orden(f):
    """Decorador para validar parámetros de ordenamiento"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ordenar_por = request.args.get('ordenar_por', 'precio')
        orden = request.args.get('orden', 'ASC').upper()
        
        campos_validos = {'precio', 'nombre', 'fecha', 'tienda', 'modelo'}
        ordenes_validos = {'ASC', 'DESC'}
        
        if ordenar_por not in campos_validos:
            abort(400, f"Campo de ordenamiento inválido. Debe ser uno de: {', '.join(campos_validos)}")
        if orden not in ordenes_validos:
            abort(400, f"Orden inválido. Debe ser uno de: {', '.join(ordenes_validos)}")
            
        return f(*args, **kwargs)
    return decorated_function

def row_to_dict(row, columns):
    """Convierte una fila SQL en un diccionario"""
    return {columns[i]: value for i, value in enumerate(row)}

@app.route('/')
@validar_parametros_orden
def index():
    """Página principal"""
    try:
        # Obtener parámetros de filtrado y ordenamiento
        tienda = request.args.get('tienda')
        modelo = request.args.get('modelo')
        ordenar_por = request.args.get('ordenar_por', 'precio')
        orden = request.args.get('orden', 'ASC')
        
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = 12  # Número de productos por página
        
        # Obtener productos con filtros y ordenamiento
        filtros = {}
        if tienda:
            filtros['tienda'] = tienda
        if modelo:
            filtros['modelo'] = modelo
            
        # Obtener todos los productos filtrados y ordenados
        todos_productos = obtener_todos_productos(filtros, ordenar_por=ordenar_por, orden=orden)
        
        # Calcular la paginación
        total_productos = len(todos_productos)
        total_pages = (total_productos + per_page - 1) // per_page
        
        # Asegurar que la página actual es válida
        page = max(1, min(page, total_pages))
        
        # Obtener los productos de la página actual
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        productos_paginados = todos_productos[start_idx:end_idx]
        
        stats = obtener_estadisticas()
        estadisticas = adaptar_estadisticas(stats)
        
        return render_template('index.html',
                           productos=productos_paginados,
                           total_productos=total_productos,
                           page=page,
                           total_pages=total_pages,
                           estadisticas=estadisticas,
                           tiendas=SITIOS_HABILITADOS,
                           modelos=MODELOS_BUSQUEDA,
                           formatear_precio=formatear_precio,
                           filtros={'tienda': tienda, 'modelo': modelo, 'ordenar_por': ordenar_por, 'orden': orden},
                           now=datetime.now())
    except Exception as e:
        logger.error(f"Error en la página principal: {e}")
        return render_template('500.html', error=str(e))

@app.route('/historial/<id_producto>')
def historial(id_producto):
    """Página de historial de precios de un producto"""
    try:
        # Obtener historial de precios
        historial = obtener_historial_precios(id_producto)
        
        if not historial:
            abort(404, "Producto no encontrado")
            
        # Preparar datos para el gráfico
        fechas = [registro['fecha'] for registro in historial]
        precios = [registro['precio'] for registro in historial]
        
        # Generar gráfico
        ruta_grafico = generar_grafico_precios(fechas, precios, id_producto)
        
        return render_template('historial.html',
                           historial=historial,
                           ruta_grafico=ruta_grafico,
                           formatear_precio=formatear_precio)
    except Exception as e:
        logger.error(f"Error al mostrar historial: {e}")
        return render_template('500.html', error=str(e))

@app.route('/api/productos')
@validar_parametros_orden
def api_productos():
    """API para obtener productos"""
    try:
        tienda = request.args.get('tienda')
        modelo = request.args.get('modelo')
        
        filtros = {}
        if tienda:
            filtros['tienda'] = tienda
        if modelo:
            filtros['modelo'] = modelo
            
        productos = obtener_todos_productos(filtros)
        return jsonify(productos)
    except Exception as e:
        logger.error(f"Error en API productos: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/actualizar')
def actualizar():
    """Actualiza los productos ejecutando el scraper"""
    try:
        ejecutar_scraper()
        return jsonify({"mensaje": "Productos actualizados correctamente"})
    except Exception as e:
        logger.error(f"Error al actualizar productos: {e}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', error="Página no encontrada"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html', error="Error interno del servidor"), 500

if __name__ == '__main__':
    app.run(debug=True)
