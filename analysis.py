# analysis.py
import sqlite3
import matplotlib.pyplot as plt
from config import DATABASE_NAME, MODELOS_BUSQUEDA, MOSTRAR_GRAFICO

def obtener_estadisticas():
    """
    Obtiene estadísticas de precios para cada modelo de GPU (RTX 4070, 4080, 4090).
    Calcula:
    - Precio mínimo, máximo y promedio.
    - Las 5 mejores ofertas (productos con precio inferior al promedio).
    """
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    estadisticas = {}
    for modelo in MODELOS_BUSQUEDA:
        c.execute('''SELECT MIN(precio), MAX(precio), AVG(precio)
                    FROM productos WHERE modelo = ?''', (f"RTX {modelo}",))
        min_price, max_price, avg_price = c.fetchone()
        
        # Selecciona las 5 mejores ofertas (productos cuyo precio es menor al promedio)
        c.execute('''SELECT nombre, precio FROM productos 
                    WHERE modelo = ? AND precio < ?
                    ORDER BY precio LIMIT 5''', (f"RTX {modelo}", avg_price))
        ofertas = c.fetchall()
        
        estadisticas[f"RTX {modelo}"] = {
            'min': min_price,
            'max': max_price,
            'avg': avg_price,
            'ofertas': ofertas
        }
    
    conn.close()
    return estadisticas

def mostrar_grafico(estadisticas):
    """
    Genera un gráfico de barras con los precios promedio de cada modelo.
    Si MOSTRAR_GRAFICO es True, se muestra el gráfico en pantalla; de lo contrario se guarda como imagen.
    """
    modelos = [f"RTX {m}" for m in MODELOS_BUSQUEDA]
    promedios = [estadisticas[f"RTX {m}"]['avg'] for m in MODELOS_BUSQUEDA]
    
    plt.bar(modelos, promedios, color='skyblue')
    plt.title('Precios Promedio de GPUs')
    plt.ylabel('Precio (MXN)')
    
    if MOSTRAR_GRAFICO:
        plt.show()
    else:
        plt.savefig('precios_promedio.png')
        plt.close()
