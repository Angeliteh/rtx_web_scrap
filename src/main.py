import time
import random
from config import MODELOS_BUSQUEDA, SITIOS_HABILITADOS
from utils import fetch_page, get_headers
from database import crear_tabla, guardar_en_db, obtener_historial_precios
from alerts import enviar_alertas

# Importación dinámica de scrapers según configuración
from scrapers.amazon_scraper import scrape_amazon_page
# Nuevos scrapers a implementar
from scrapers.mercadolibre_scraper import scrape_mercadolibre_page
from scrapers.newegg_scraper import scrape_newegg_page
from scrapers.bestbuy_scraper import scrape_bestbuy_page
from scrapers.aliexpress_scraper import scrape_aliexpress_page

def ejecutar_scraper():
    """
    Ejecuta el proceso de scraping y almacena los datos en la base de datos.
    Se puede llamar desde Flask o ejecutarlo manualmente.
    """
    crear_tabla()
    todos_productos = []

    # Mapa de funciones de scraping por sitio
    scrapers = {
        'amazon': {'func': scrape_amazon_page, 'url_template': "https://www.amazon.com.mx/s?k=rtx+{}"},
        'mercadolibre': {'func': scrape_mercadolibre_page, 'url_template': "https://listado.mercadolibre.com.mx/rtx-{}"},
        'newegg': {'func': scrape_newegg_page, 'url_template': "https://www.newegg.com/p/pl?d=rtx+{}"},
        'bestbuy': {'func': scrape_bestbuy_page, 'url_template': "https://www.bestbuy.com.mx/c/videocards/buscar/rtx+{}"},
        'aliexpress': {'func': scrape_aliexpress_page, 'url_template': "https://es.aliexpress.com/wholesale?SearchText=rtx+{}"}
    }
    
    # Iterar sobre cada sitio habilitado y modelo de GPU
    for sitio in SITIOS_HABILITADOS:
        if sitio not in scrapers:
            print(f"⚠️ Sitio {sitio} no implementado. Omitiendo...")
            continue
            
        for modelo in MODELOS_BUSQUEDA:
            scraper_info = scrapers[sitio]
            print(f"🔍 Buscando RTX {modelo} en {sitio.capitalize()}...")
            
            url = scraper_info['url_template'].format(modelo)
            html_content = fetch_page(url)

            if html_content:
                # Obtener productos del sitio
                productos = scraper_info['func'](html_content)
                
                # Para cada producto, verificar si hay cambios de precio significativos
                for producto in productos:
                    # Obtener historial de precios para verificar cambios
                    historial = obtener_historial_precios(producto['id_producto'], limite=2)
                    
                    # Si hay historial suficiente, verificar si se debe enviar alerta
                    if len(historial) >= 2:
                        precio_anterior = historial[1]['precio']
                        
                        # Enviar alertas si es necesario
                        enviar_alertas(producto, precio_anterior)
                
                # Guardar productos en la base de datos
                guardar_en_db(productos)
                todos_productos.extend(productos)
                
                # Delay aleatorio entre peticiones
                time.sleep(random.uniform(2, 5))
                
    print("✅ Scraping completado y datos almacenados en la base de datos.")
    return todos_productos

# Si se ejecuta directamente este archivo, correrá el scraper
if __name__ == "__main__":
    ejecutar_scraper()
