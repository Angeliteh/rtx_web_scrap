# analysis.py
import sqlite3
import matplotlib
# Configurar matplotlib para no usar GUI
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from src.config.config import DATABASE_NAME, MODELOS_BUSQUEDA, MOSTRAR_GRAFICO
import os

def generar_grafico_precios(fechas, precios, nombre_producto):
    """
    Genera un gráfico de línea con el historial de precios de un producto.
    
    Args:
        fechas (list): Lista de fechas
        precios (list): Lista de precios correspondientes a las fechas
        nombre_producto (str): Nombre del producto para el título del gráfico
        
    Returns:
        str: Ruta del archivo del gráfico generado (relativa a /static)
    """
    try:
        # Limpiar cualquier figura existente
        plt.clf()
        
        if not fechas or not precios:
            raise ValueError("No hay datos suficientes para generar el gráfico")
        
        # Convertir fechas a formato adecuado si son strings
        fechas_formateadas = []
        for fecha in fechas:
            if isinstance(fecha, str):
                try:
                    # Intentar convertir la fecha si es un string ISO
                    fecha_dt = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
                    fechas_formateadas.append(fecha_dt.strftime('%d/%m/%Y'))
                except (ValueError, AttributeError):
                    # Si no se puede convertir, usar el string original
                    fechas_formateadas.append(fecha)
            else:
                # Si ya es un objeto datetime, formatearlo
                if isinstance(fecha, datetime):
                    fechas_formateadas.append(fecha.strftime('%d/%m/%Y'))
                else:
                    fechas_formateadas.append(str(fecha))
            
        plt.figure(figsize=(10, 6))
        plt.plot(fechas_formateadas, precios, marker='o')
        
        # Configurar el gráfico
        titulo_corto = nombre_producto[:50] + '...' if len(nombre_producto) > 50 else nombre_producto
        plt.title(f'Historial de Precios - {titulo_corto}')
        plt.xlabel('Fecha')
        plt.ylabel('Precio (MXN)')
        plt.grid(True)
        
        # Rotar las etiquetas de fecha para mejor legibilidad
        plt.xticks(rotation=45)
        
        # Ajustar el layout para que no se corten las etiquetas
        plt.tight_layout()
        
        # Asegurar que el directorio existe
        os.makedirs('src/static/img', exist_ok=True)
        
        # Guardar el gráfico
        ruta_fisica = 'src/static/img/grafico_precios.png'
        plt.savefig(ruta_fisica)
        plt.close('all')  # Cerrar todas las figuras para liberar memoria
        
        return 'img/grafico_precios.png'
    except Exception as e:
        print(f"Error generando gráfico: {e}")
        # Generar un gráfico de error
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, 'Error generando gráfico\nNo hay suficientes datos', 
                horizontalalignment='center', verticalalignment='center')
        plt.axis('off')
        
        ruta_fisica = 'src/static/img/grafico_error.png'
        plt.savefig(ruta_fisica)
        plt.close('all')
        return 'img/grafico_error.png'

def obtener_estadisticas():
    """
    Obtiene estadísticas de precios para cada modelo de GPU.
    Maneja casos donde no hay datos o hay valores nulos.
    """
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        
        estadisticas = {
            'total_productos': 0,
            'min_precio': float('inf'),
            'max_precio': 0,
            'avg_precio': 0,
            'por_modelo': {}
        }
        
        # Obtener estadísticas generales
        c.execute('''SELECT COUNT(*), MIN(precio), MAX(precio), AVG(precio)
                    FROM productos WHERE precio > 0''')
        total, min_price, max_price, avg_price = c.fetchone()
        
        if total and total > 0:
            estadisticas.update({
                'total_productos': total,
                'min_precio': min_price or 0,
                'max_precio': max_price or 0,
                'avg_precio': avg_price or 0
            })
        
        # Estadísticas por modelo
        for modelo in MODELOS_BUSQUEDA:
            modelo_completo = f"RTX {modelo}"
            c.execute('''SELECT COUNT(*), MIN(precio), MAX(precio), AVG(precio)
                        FROM productos 
                        WHERE modelo = ? AND precio > 0''', (modelo_completo,))
            total, min_price, max_price, avg_price = c.fetchone()
            
            # Seleccionar las 5 mejores ofertas
            c.execute('''SELECT nombre, precio, vendedor 
                        FROM productos 
                        WHERE modelo = ? AND precio > 0
                        ORDER BY precio ASC LIMIT 5''', (modelo_completo,))
            ofertas = [{'nombre': n, 'precio': p, 'vendedor': v} for n, p, v in c.fetchall()]
            
            estadisticas['por_modelo'][modelo_completo] = {
                'total': total or 0,
                'min': min_price or 0,
                'max': max_price or 0,
                'avg': avg_price or 0,
                'ofertas': ofertas
            }
        
        conn.close()
        return estadisticas
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")
        return {
            'total_productos': 0,
            'min_precio': 0,
            'max_precio': 0,
            'avg_precio': 0,
            'por_modelo': {},
            'error': str(e)
        }

def mostrar_grafico(estadisticas):
    """
    Genera un gráfico de barras con los precios promedio de cada modelo.
    """
    try:
        plt.clf()
        modelos = []
        promedios = []
        
        for modelo, stats in estadisticas['por_modelo'].items():
            if stats['avg'] > 0:  # Solo incluir modelos con datos válidos
                modelos.append(modelo)
                promedios.append(stats['avg'])
        
        if not modelos:
            raise ValueError("No hay datos suficientes para generar el gráfico")
        
        plt.figure(figsize=(10, 6))
        plt.bar(modelos, promedios, color='skyblue')
        plt.title('Precios Promedio de GPUs')
        plt.ylabel('Precio (MXN)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        ruta_fisica = 'src/static/img/precios_promedio.png'
        plt.savefig(ruta_fisica)
        plt.close('all')
        
        return 'img/precios_promedio.png'
    except Exception as e:
        print(f"Error generando gráfico de promedios: {e}")
        return None
