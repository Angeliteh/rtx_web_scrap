# app.py
from flask import Flask, render_template, request, jsonify, abort
from datetime import datetime
from functools import wraps
import logging


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
    try:
        # Verificar si hay estadísticas
        if not stats or not isinstance(stats, dict):
            return {
                "total_productos": 0,
                "min_precio": 0,
                "max_precio": 0,
                "avg_precio": 0
            }
            
        # Obtenemos todos los precios
        precios = []
        
        # Intentar obtener precios de diferentes fuentes en el diccionario
        if 'min_precio' in stats and isinstance(stats['min_precio'], (int, float)):
            precios.append(stats['min_precio'])
            
        if 'max_precio' in stats and isinstance(stats['max_precio'], (int, float)):
            precios.append(stats['max_precio'])
            
        # Buscar precios en el diccionario por_modelo
        for modelo, datos in stats.get("por_modelo", {}).items():
            if isinstance(datos, dict):
                # Agregar precios mínimos y máximos si existen
                if 'min' in datos and datos['min'] and datos['min'] > 0:
                    precios.append(datos['min'])
                if 'max' in datos and datos['max'] and datos['max'] > 0:
                    precios.append(datos['max'])
                    
        # Buscar precios en los diccionarios precio_minimo y precio_maximo
        for modelo, precio in stats.get("precio_minimo", {}).items():
            if precio and precio > 0:
                precios.append(precio)
                
        for modelo, precio in stats.get("precio_maximo", {}).items():
            if precio and precio > 0:
                precios.append(precio)
        
        # Calcular estadísticas globales
        resultado = {
            "total_productos": stats.get("total_productos", 0),
            "min_precio": min(precios) if precios else 0,
            "max_precio": max(precios) if precios else 0,
            "avg_precio": sum(precios) / len(precios) if precios else 0
        }
        
        return resultado
    except Exception as e:
        logger.error(f"Error adaptando estadísticas: {e}")
        return {
            "total_productos": 0,
            "min_precio": 0,
            "max_precio": 0,
            "avg_precio": 0
        }

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
        # Asegurar que total_pages sea al menos 1
        total_pages = ((total_productos + per_page - 1) // per_page) if total_productos > 0 else 1
        
        # Asegurar que la página actual esté dentro de los límites válidos
        if page < 1:
            page = 1
        if page > total_pages:
            page = total_pages
        
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
        # Obtener historial de precios e información del producto
        historial, info_producto = obtener_historial_precios(id_producto)
        
        if not info_producto:
            return render_template('404.html', 
                                error="Producto no encontrado",
                                mensaje="El producto que buscas no existe o ha sido eliminado.")
        
        if not historial:
            return render_template('historial.html',
                               producto=info_producto,
                               historial=[],
                               mensaje="Este producto aún no tiene historial de precios registrado.",
                               ruta_grafico=None,
                               formatear_precio=formatear_precio,
                               now=datetime.now())
            
        # Preparar datos para el gráfico
        fechas = [registro['fecha'] for registro in historial]
        precios = [registro['precio'] for registro in historial]
        
        # Generar gráfico
        try:
            ruta_grafico = generar_grafico_precios(fechas, precios, info_producto['nombre'])
        except Exception as e:
            logger.error(f"Error generando gráfico: {e}")
            ruta_grafico = None
        
        # Calcular estadísticas del historial
        if precios:
            precio_actual = precios[-1] if precios else 0
            precio_promedio = sum(precios) / len(precios)
            
            # Calcular tendencia (últimos 30 días o todos si hay menos)
            precios_recientes = precios[-30:] if len(precios) > 30 else precios
            if len(precios_recientes) > 1:
                tendencia = (precios_recientes[-1] - precios_recientes[0]) / precios_recientes[0] * 100
            else:
                tendencia = 0
            
            # Calcular variación 30 días
            if len(precios) > 30:
                variacion_30d = ((precios[-1] - precios[-30]) / precios[-30] * 100)
            else:
                variacion_30d = 0
            
            # Determinar mejor momento para comprar
            precio_promedio_30d = sum(precios_recientes) / len(precios_recientes)
            if precio_actual < precio_promedio_30d:
                mejor_momento = "Buen momento para comprar"
            elif tendencia < -5:
                mejor_momento = "Esperar (precio bajando)"
            else:
                mejor_momento = "Precio por encima del promedio"
            
            # Calcular diferencia con el promedio
            diferencia_promedio = ((precio_actual - precio_promedio) / precio_promedio * 100)
            
            # Encontrar fechas de precios mínimo y máximo
            idx_min = precios.index(min(precios))
            idx_max = precios.index(max(precios))
            fecha_precio_minimo = fechas[idx_min]
            fecha_precio_maximo = fechas[idx_max]
            
            estadisticas_historial = {
                'precio_minimo': min(precios),
                'precio_maximo': max(precios),
                'precio_promedio': precio_promedio,
                'total_registros': len(precios)
            }
            
            # Calcular cambios porcentuales para el historial
            for i in range(len(historial)):
                if i > 0:
                    precio_anterior = historial[i-1]['precio']
                    precio_actual = historial[i]['precio']
                    cambio = ((precio_actual - precio_anterior) / precio_anterior * 100)
                    historial[i]['cambio'] = round(cambio, 2)
                else:
                    historial[i]['cambio'] = 0
                    
        else:
            estadisticas_historial = None
            tendencia = 0
            variacion_30d = 0
            mejor_momento = "Sin datos suficientes"
            diferencia_promedio = 0
            precio_actual = 0
            fecha_precio_minimo = "Sin datos"
            fecha_precio_maximo = "Sin datos"
        
        return render_template('historial.html',
                           producto=info_producto,
                           historial=historial,
                           ruta_grafico=ruta_grafico,
                           estadisticas=estadisticas_historial,
                           tendencia=tendencia,
                           variacion_30d=round(variacion_30d, 2),
                           mejor_momento=mejor_momento,
                           diferencia_promedio=round(diferencia_promedio, 2),
                           precio_actual=precio_actual,
                           fecha_precio_minimo=fecha_precio_minimo,
                           fecha_precio_maximo=fecha_precio_maximo,
                           formatear_precio=formatear_precio,
                           now=datetime.now())
                           
    except Exception as e:
        logger.error(f"Error al mostrar historial: {e}")
        return render_template('500.html', 
                             error="Error al cargar el historial",
                             mensaje=str(e),
                             now=datetime.now())

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
    return render_template('404.html', 
                          error="Página no encontrada", 
                          now=datetime.now()), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html', 
                          error="Error interno del servidor", 
                          now=datetime.now()), 500

if __name__ == '__main__':
    app.run(debug=True)
