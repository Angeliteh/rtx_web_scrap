# main.py
import time
import random
from config import MODELOS_BUSQUEDA
from utils import fetch_page, get_headers
from amazon_scraper import scrape_amazon_page
from database import crear_tabla, guardar_en_db
from analysis import obtener_estadisticas, mostrar_grafico
from filters import filtrar_productos_por_busqueda

def main():
    """
    Flujo general:
      1. Se crea la base de datos y la tabla si no existen.
      2. Por cada modelo en MODELOS_BUSQUEDA, se genera la URL de búsqueda y se obtiene el HTML.
      3. Se realiza el scraping de la página de Amazon con scrape_amazon_page.
      4. Los productos extraídos se guardan en la base de datos.
      5. Se realiza un ejemplo de filtrado (por ejemplo, productos que contengan 'super').
      6. Se generan estadísticas (mínimo, máximo, promedio y mejores ofertas).
      7. Se muestra o guarda un gráfico de barras con los precios promedio.
    """
    crear_tabla()
    todos_productos = []
    
    for modelo in MODELOS_BUSQUEDA:
        print(f"Buscando RTX {modelo} en Amazon...")
        url = f"https://www.amazon.com.mx/s?k=rtx+{modelo}"
        html_content = fetch_page(url)
        
        if html_content:
            productos = scrape_amazon_page(html_content)
            guardar_en_db(productos)
            todos_productos.extend(productos)
            time.sleep(random.uniform(2, 5))  # Delay aleatorio para evitar bloqueos
    
    # Ejemplo de filtrado: filtrar productos que contengan 'super'
    filtro = "super"
    productos_filtrados = filtrar_productos_por_busqueda(todos_productos, filtro)
    print(f"\nProductos filtrados con '{filtro}':")
    for p in productos_filtrados:
        print(f"Nombre: {p['nombre']}\nPrecio: ${p['precio']}\nLink: {p['link']}\nImagen: {p['imagen']}\n")
    
    # Generar y mostrar estadísticas
    stats = obtener_estadisticas()
    for modelo, data in stats.items():
        print(f"\nEstadísticas para {modelo}:")
        print(f"Precio mínimo: ${data['min']}")
        print(f"Precio máximo: ${data['max']}")
        print(f"Precio promedio: ${data['avg']:.2f}")
        print("Mejores ofertas:")
        for oferta in data['ofertas']:
            print(f"- {oferta[0]} (${oferta[1]})")
    
    # Mostrar o guardar el gráfico de precios promedio
    #mostrar_grafico(stats)

if __name__ == "__main__":
    main()
